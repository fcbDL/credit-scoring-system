"""Semantic analysis agent for credit scoring.

This agent is responsible for analyzing unstructured text data
such as credit remarks, consumption behavior descriptions, and
loan application statements to identify potential risks.
"""

import json
from typing import Optional

from ...llm import LLMClient
from ...schema import Message
from ...tools.base import Tool
from ..state import CreditState, SemanticRisk


class SemanticAgent:
    """Agent for semantic risk analysis.

    This agent:
    1. Analyzes text data (credit remarks, application statements)
    2. Identifies fraud indicators
    3. Evaluates repayment willingness
    4. Assesses industry risk
    """

    def __init__(
        self,
        llm_client: LLMClient,
        tools: list[Tool],
    ):
        """Initialize semantic agent.

        Args:
            llm_client: LLM client for text analysis
            tools: List of tools available to this agent
        """
        self.llm = llm_client
        self.tools = {tool.name: tool for tool in tools}

    async def run(self, state: CreditState) -> CreditState:
        """Run semantic analysis.

        Args:
            state: Current workflow state

        Returns:
            Updated state with semantic analysis results
        """
        # Extract text data from state
        text_data = state.get("text_data", {})
        application_statement = text_data.get("application_statement", "")
        credit_remarks = text_data.get("credit_remarks", "")

        if not application_statement and not credit_remarks:
            state["trace"].append({
                "agent": "semantic",
                "action": "skip",
                "reason": "No text data provided",
            })
            return state

        try:
            # First, retrieve relevant regulations if RAG is available
            rag_results = []
            rag_tool = self.tools.get("rag_retrieval")
            if rag_tool and application_statement:
                # Extract key risk-related terms for better RAG matching
                query_terms = []
                if "逾期" in application_statement or "欠款" in application_statement:
                    query_terms.append("逾期")
                if "收入" in application_statement or "工资" in application_statement:
                    query_terms.append("收入")
                if "负债" in application_statement or "债务" in application_statement:
                    query_terms.append("负债率")
                if "经营" in application_statement or "生意" in application_statement:
                    query_terms.append("经营风险")
                if "房产" in application_statement or "抵押" in application_statement:
                    query_terms.append("抵押担保")

                # Default query if no specific terms found
                if not query_terms:
                    query_terms = ["贷款风险", "信贷审批"]
                else:
                    query_terms.append("贷款风险")

                query = " ".join(query_terms)
                rag_result = await rag_tool.execute(
                    query=query,
                    top_k=3,
                )
                if rag_result.success:
                    rag_results = json.loads(rag_result.content)
                    state["trace"].append({
                        "agent": "semantic",
                        "action": "rag_retrieval",
                        "query": query,
                        "results_count": len(rag_results),
                    })

            # Use LLM for semantic analysis
            analysis_prompt = self._build_analysis_prompt(
                application_statement=application_statement,
                credit_remarks=credit_remarks,
                rag_results=rag_results,
            )

            messages = [
                Message(
                    role="system",
                    content="你是一个专业的信贷分析师，负责客观分析借款人的申请文本，评估还款能力和信用风险。要同时关注正面信息和风险点，客观评估。",
                ),
                Message(role="user", content=analysis_prompt),
            ]

            response = await self.llm.generate(messages=messages)

            # Parse LLM response into structured format
            semantic_risk = self._parse_analysis_response(response.content)

            state["semantic_risk"] = semantic_risk.model_dump()
            state["trace"].append({
                "agent": "semantic",
                "action": "llm_analysis",
                "result": f"Fraud indicators: {len(semantic_risk.fraud_indicators)}, "
                          f"Repayment willingness: {semantic_risk.repayment_willingness}, "
                          f"Industry risk: {semantic_risk.industry_risk}",
            })

        except Exception as e:
            state["errors"].append(f"Semantic agent error: {str(e)}")
            state["trace"].append({
                "agent": "semantic",
                "action": "error",
                "error": str(e),
            })

        return state

    def _build_analysis_prompt(
        self,
        application_statement: str,
        credit_remarks: str,
        rag_results: list,
    ) -> str:
        """Build analysis prompt for LLM."""
        prompt = "请分析以下借款人的信贷申请文本，识别潜在风险：\n\n"

        if application_statement:
            prompt += f"【贷款申请陈述】\n{application_statement}\n\n"

        if credit_remarks:
            prompt += f"【征信备注】\n{credit_remarks}\n\n"

        if rag_results:
            prompt += "【相关法规参考】\n"
            for i, r in enumerate(rag_results, 1):
                prompt += f"{i}. {r.get('title', 'N/A')}: {r.get('content', '')[:200]}...\n"
            prompt += "\n"

        prompt += """请以JSON格式返回分析结果：
{
    "fraud_indicators": ["仅列出真正高风险的欺诈指标，不要过度解读"],
    "repayment_willingness": "high/medium/low",
    "industry_risk": "low/medium/high",
    "positive_factors": ["列出申请人的优势，如稳定收入、良好信用历史等"],
    "confidence": 0.85
}

注意：
1. 只列出真正的高风险欺诈指标，不要把正常的申请描述当成欺诈
2. 如果申请信息基本正常，fraud_indicators 应为空数组
3. 只返回JSON，不要其他内容。"""

        return prompt

    def _parse_analysis_response(self, response: str) -> SemanticRisk:
        """Parse LLM response into SemanticRisk model."""
        try:
            # Try to extract JSON from response
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return SemanticRisk(
                    fraud_indicators=data.get("fraud_indicators", []),
                    repayment_willingness=data.get("repayment_willingness", "medium"),
                    industry_risk=data.get("industry_risk", "medium"),
                    concerns=data.get("concerns", []),
                    confidence=data.get("confidence", 0.5),
                )
        except Exception:
            pass

        # Return default if parsing fails
        return SemanticRisk(
            fraud_indicators=[],
            repayment_willingness="medium",
            industry_risk="medium",
            concerns=["分析失败"],
            confidence=0.0,
        )
