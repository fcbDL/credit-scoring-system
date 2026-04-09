"""
FastAPI backend for Credit Scoring Multi-Agent System.

Run with:
    uvicorn mini_agent.web.api:app --reload
"""

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import multi-agent components
from mini_agent.multi_agent import create_credit_graph
from mini_agent.multi_agent.agents import NumericAgent, SemanticAgent, SupervisorAgent
from mini_agent.multi_agent.state import CreditState
from mini_agent.tools.credit_tools import XGBoostScoreTool, RiskRuleEngineTool, RAGRetrievalTool
from mini_agent.llm import LLMClient
from mini_agent.schema import LLMProvider
from mini_agent.config import Config
from mini_agent.retry import RetryConfig
from mini_agent.database import (
    save_evaluation,
    get_evaluations,
    get_evaluation_by_id,
    get_statistics,
)

app = FastAPI(title="信贷评分 API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class CreditEvaluateRequest(BaseModel):
    """Credit evaluation request."""
    user_input: Optional[str] = ""
    user_id: Optional[str] = None
    numeric_data: Optional[dict[str, Any]] = None
    text_data: Optional[dict[str, Any]] = None


class CreditEvaluateResponse(BaseModel):
    """Credit evaluation response."""
    final_decision: str
    decision_reason: str
    numeric_result: Optional[dict] = None
    semantic_risk: Optional[dict] = None
    conflict_detected: bool = False
    conflict_details: Optional[str] = None
    trace: list = []
    credit_report: Optional[dict] = None


class BatchEvaluateRequest(BaseModel):
    """Batch evaluation request."""
    applications: list[CreditEvaluateRequest]


class BatchEvaluateResponse(BaseModel):
    """Batch evaluation response."""
    total: int
    success: int
    failed: int
    results: list[CreditEvaluateResponse]


# Global graph instance (lazy initialization)
_graph = None
_llm_client = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client."""
    global _llm_client
    if _llm_client is None:
        config_path = Config.get_default_config_path()
        config = Config.from_yaml(config_path)

        retry_config = RetryConfig(
            enabled=config.llm.retry.enabled,
            max_retries=config.llm.retry.max_retries,
            initial_delay=config.llm.retry.initial_delay,
            max_delay=config.llm.retry.max_delay,
            exponential_base=config.llm.retry.exponential_base,
            retryable_exceptions=(Exception,),
        )

        provider = LLMProvider.ANTHROPIC if config.llm.provider.lower() == "anthropic" else LLMProvider.OPENAI

        _llm_client = LLMClient(
            api_key=config.llm.api_key,
            provider=provider,
            api_base=config.llm.api_base,
            model=config.llm.model,
            retry_config=retry_config if config.llm.retry.enabled else None,
        )
    return _llm_client


def get_graph():
    """Get or create LangGraph workflow."""
    global _graph
    if _graph is None:
        llm_client = get_llm_client()

        # Initialize tools
        tools = [
            XGBoostScoreTool(),
            RiskRuleEngineTool(),
            RAGRetrievalTool(),
        ]

        # Initialize agents
        numeric_agent = NumericAgent(llm_client=llm_client, tools=tools)
        semantic_agent = SemanticAgent(llm_client=llm_client, tools=tools)
        supervisor_agent = SupervisorAgent(llm_client=llm_client, tools=tools)

        # Create graph
        _graph = create_credit_graph(
            numeric_agent=numeric_agent,
            semantic_agent=semantic_agent,
            supervisor_agent=supervisor_agent,
        )

    return _graph


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "信贷评分 API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


@app.post("/api/credit/evaluate", response_model=CreditEvaluateResponse)
async def evaluate_credit(request: CreditEvaluateRequest, save_record: bool = True):
    """Evaluate credit application.

    Args:
        request: Credit evaluation request
        save_record: Whether to save to database (default True)
    """
    try:
        # Get graph
        graph = get_graph()

        # Build initial state
        initial_state: CreditState = {
            "user_input": request.user_input or "贷款申请评估",
            "user_id": request.user_id,
            "numeric_data": request.numeric_data,
            "text_data": request.text_data,
            "numeric_result": None,
            "semantic_risk": None,
            "conflict_detected": False,
            "conflict_details": None,
            "audit_result": None,
            "audit_iterations": 0,
            "final_decision": "",
            "decision_reason": "",
            "trace": [],
            "errors": [],
        }

        # Run workflow
        result = await graph.ainvoke(initial_state)

        # Save to database if requested
        if save_record and request.numeric_data:
            try:
                numeric_result = result.get("numeric_result", {})
                save_evaluation(
                    user_id=request.user_id,
                    user_input=request.user_input or "贷款申请评估",
                    numeric_data=request.numeric_data or {},
                    text_data=request.text_data or {},
                    final_decision=result.get("final_decision", ""),
                    decision_reason=result.get("decision_reason", ""),
                    numeric_result=numeric_result,
                    semantic_risk=result.get("semantic_risk", {}),
                    credit_score=numeric_result.get("credit_score", 0),
                    risk_level=numeric_result.get("risk_level", "unknown"),
                    conflict_detected=result.get("conflict_detected", False),
                    trace=result.get("trace", []),
                )
            except Exception as db_err:
                print(f"[DB] Failed to save: {db_err}")

        # Return response
        return CreditEvaluateResponse(
            final_decision=result.get("final_decision", ""),
            decision_reason=result.get("decision_reason", ""),
            numeric_result=result.get("numeric_result"),
            semantic_risk=result.get("semantic_risk"),
            conflict_detected=result.get("conflict_detected", False),
            conflict_details=result.get("conflict_details"),
            trace=result.get("trace", []),
            credit_report=result.get("credit_report"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 评估历史 API ==========

@app.get("/api/evaluations")
async def list_evaluations(
    limit: int = 50,
    offset: int = 0,
    user_id: Optional[str] = None,
):
    """Get evaluation history list."""
    try:
        evaluations = get_evaluations(limit=limit, offset=offset, user_id=user_id)
        return {"evaluations": evaluations, "total": len(evaluations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/evaluations/{eval_id}")
async def get_evaluation(eval_id: int):
    """Get evaluation details by ID."""
    try:
        evaluation = get_evaluation_by_id(eval_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        return evaluation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/evaluations/statistics")
async def get_eval_statistics():
    """Get evaluation statistics."""
    try:
        stats = get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 批量评估 API ==========

@app.post("/api/credit/batch-evaluate", response_model=BatchEvaluateResponse)
async def batch_evaluate_credit(request: BatchEvaluateRequest):
    """Batch evaluate multiple credit applications."""
    results = []
    success_count = 0
    failed_count = 0

    graph = get_graph()

    for idx, app in enumerate(request.applications):
        try:
            initial_state: CreditState = {
                "user_input": app.user_input or "批量贷款评估",
                "user_id": app.user_id,
                "numeric_data": app.numeric_data,
                "text_data": app.text_data,
                "numeric_result": None,
                "semantic_risk": None,
                "conflict_detected": False,
                "conflict_details": None,
                "audit_result": None,
                "audit_iterations": 0,
                "final_decision": "",
                "decision_reason": "",
                "trace": [],
                "errors": [],
            }

            result = await graph.ainvoke(initial_state)

            results.append(CreditEvaluateResponse(
                final_decision=result.get("final_decision", ""),
                decision_reason=result.get("decision_reason", ""),
                numeric_result=result.get("numeric_result"),
                semantic_risk=result.get("semantic_risk"),
                conflict_detected=result.get("conflict_detected", False),
                conflict_details=result.get("conflict_details"),
                trace=result.get("trace", []),
                credit_report=result.get("credit_report"),
            ))
            success_count += 1

        except Exception as e:
            failed_count += 1
            results.append(CreditEvaluateResponse(
                final_decision="error",
                decision_reason=f"评估失败: {str(e)}",
                numeric_result=None,
                semantic_risk=None,
                conflict_detected=False,
                trace=[],
            ))

    return BatchEvaluateResponse(
        total=len(request.applications),
        success=success_count,
        failed=failed_count,
        results=results,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
