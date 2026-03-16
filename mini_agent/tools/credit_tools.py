"""Credit domain specific tools for the multi-agent system.

This module provides tools for:
- XGBoost model inference
- RAG retrieval from knowledge base
- Risk rule engine matching
"""

import json
from typing import Any, Optional
from pydantic import BaseModel, Field

from .base import Tool, ToolResult


class XGBoostScoreInput(BaseModel):
    """Input schema for XGBoost scoring."""

    age: int = Field(description="Applicant age")
    income: float = Field(description="Annual income")
    credit_history_length: int = Field(description="Credit history length in years")
    debt_to_income_ratio: float = Field(description="Debt to income ratio (0-1)")
    employment_length: int = Field(description="Employment length in years")
    loan_amount: float = Field(description="Requested loan amount")
    loan_purpose: str = Field(description="Loan purpose: personal/business/education/home")
    existing_loans: int = Field(description="Number of existing loans")
    payment_history: float = Field(description="Payment history score (0-1)")


class XGBoostScoreTool(Tool):
    """Tool to run XGBoost model for credit scoring.

    This tool wraps a pre-trained XGBoost model and returns
    credit score and risk assessment.
    """

    def __init__(self, model_path: Optional[str] = None):
        """Initialize XGBoost scoring tool.

        Args:
            model_path: Path to pre-trained XGBoost model (optional, uses default if None)
        """
        self.model_path = model_path
        self._model = None

    @property
    def name(self) -> str:
        return "xgboost_credit_score"

    @property
    def description(self) -> str:
        return (
            "Run XGBoost model to calculate credit score based on structured numerical data. "
            "Returns credit score (0-100), probability of default, and risk level. "
            "Use this for numerical credit assessment."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "age": {"type": "integer", "description": "Applicant age"},
                "income": {"type": "number", "description": "Annual income"},
                "credit_history_length": {"type": "integer", "description": "Credit history length in years"},
                "debt_to_income_ratio": {"type": "number", "description": "Debt to income ratio (0-1)"},
                "employment_length": {"type": "integer", "description": "Employment length in years"},
                "loan_amount": {"type": "number", "description": "Requested loan amount"},
                "loan_purpose": {
                    "type": "string",
                    "enum": ["personal", "business", "education", "home"],
                    "description": "Loan purpose",
                },
                "existing_loans": {"type": "integer", "description": "Number of existing loans"},
                "payment_history": {"type": "number", "description": "Payment history score (0-1)"},
            },
            "required": ["age", "income", "credit_history_length", "debt_to_income_ratio"],
        }

    def _load_model(self):
        """Load XGBoost model (lazy loading)."""
        if self._model is None:
            # Placeholder: In production, load actual model
            # import xgboost as xgb
            # self._model = xgb.Booster()
            # self._model.load_model(self.model_path or "models/credit_xgboost.json")
            pass
        return self._model

    async def execute(self, **kwargs) -> ToolResult:
        """Execute XGBoost scoring."""
        try:
            # Validate input
            validated = XGBoostScoreInput(**kwargs)

            # Placeholder: In production, run actual model prediction
            # model = self._load_model()
            # dmatrix = xgb.DMatrix([validated.model_dump()])
            # prediction = model.predict(dmatrix)

            # Simulated response for development
            score = self._calculate_mock_score(validated)
            prob_default = max(0.01, min(0.99, (100 - score) / 100))

            result = {
                "credit_score": score,
                "probability_default": round(prob_default, 4),
                "risk_level": "low" if score >= 70 else "medium" if score >= 50 else "high",
                "features_importance": {
                    "payment_history": 0.25,
                    "debt_to_income_ratio": 0.20,
                    "credit_history_length": 0.18,
                    "income": 0.15,
                    "employment_length": 0.12,
                    "age": 0.05,
                    "loan_amount": 0.03,
                    "existing_loans": 0.02,
                },
            }

            return ToolResult(
                success=True,
                content=json.dumps(result, indent=2, ensure_ascii=False),
            )

        except Exception as e:
            return ToolResult(success=False, content="", error=f"XGBoost scoring failed: {str(e)}")

    def _calculate_mock_score(self, data: XGBoostScoreInput) -> float:
        """Calculate mock score for development (replace with real model)."""
        base_score = 50.0

        # Credit history bonus
        base_score += min(data.credit_history_length * 3, 15)

        # Payment history bonus
        base_score += data.payment_history * 20

        # Employment bonus
        base_score += min(data.employment_length * 2, 10)

        # Income impact (normalized)
        if data.income > 100000:
            base_score += 10
        elif data.income > 50000:
            base_score += 5

        # Debt ratio penalty
        base_score -= data.debt_to_income_ratio * 20

        # Age impact
        if 25 <= data.age <= 55:
            base_score += 5

        return max(0, min(100, base_score))


class RAGRetrievalTool(Tool):
    """Tool for RAG (Retrieval Augmented Generation) from knowledge base.

    Retrieves relevant financial regulations and risk cases for
    compliance checking and risk assessment.
    """

    def __init__(self, knowledge_base_path: Optional[str] = None):
        """Initialize RAG retrieval tool.

        Args:
            knowledge_base_path: Path to knowledge base (optional)
        """
        self.knowledge_base_path = knowledge_base_path

    @property
    def name(self) -> str:
        return "rag_retrieval"

    @property
    def description(self) -> str:
        return (
            "Retrieve relevant financial regulations, compliance rules, and "
            "similar risk cases from the knowledge base. Use this for compliance "
            "checking and finding precedents."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "top_k": {"type": "integer", "description": "Number of results to return", "default": 5},
                "category": {
                    "type": "string",
                    "enum": ["regulation", "risk_case", "compliance", "all"],
                    "description": "Category to search",
                    "default": "all",
                },
            },
            "required": ["query"],
        }

    async def execute(self, query: str, top_k: int = 5, category: str = "all") -> ToolResult:
        """Execute RAG retrieval."""
        try:
            # Placeholder: In production, use actual vector DB (Milvus/Chroma)
            # results = vector_db.search(query, top_k=top_k, filter=category)

            # Simulated response for development
            results = [
                {
                    "title": "个人信贷风险管理指引",
                    "content": "金融机构应建立完善的个人信贷风险评估体系...",
                    "source": "银保监会规定",
                    "relevance": 0.95,
                },
                {
                    "title": "贷款审批合规要求",
                    "content": "贷款审批应遵循审慎原则，确保借款人具备还款能力...",
                    "source": "内部合规手册",
                    "relevance": 0.88,
                },
            ]

            return ToolResult(
                success=True,
                content=json.dumps(results[:top_k], indent=2, ensure_ascii=False),
            )

        except Exception as e:
            return ToolResult(success=False, content="", error=f"RAG retrieval failed: {str(e)}")


class RiskRuleEngineTool(Tool):
    """Tool for matching risk rules.

    Evaluates applicant against predefined hard rules (regulatory requirements,
    internal policies) that must be satisfied.
    """

    def __init__(self):
        """Initialize risk rule engine."""
        self.rules = self._load_rules()

    def _load_rules(self) -> list[dict[str, Any]]:
        """Load risk rules (placeholder)."""
        return [
            {
                "id": "rule_001",
                "name": "负债率上限",
                "condition": "debt_to_income_ratio > 0.7",
                "action": "reject",
                "description": "负债率超过70%直接拒绝",
            },
            {
                "id": "rule_002",
                "name": "年龄范围",
                "condition": "age < 18 or age > 70",
                "action": "reject",
                "description": "年龄不在18-70岁范围内拒绝",
            },
            {
                "id": "rule_003",
                "name": "信用记录要求",
                "condition": "credit_history_length < 1",
                "action": "review",
                "description": "信用记录少于1年需要人工复核",
            },
            {
                "id": "rule_004",
                "name": "收入要求",
                "condition": "income < 10000",
                "action": "reject",
                "description": "年收入低于1万元拒绝",
            },
        ]

    @property
    def name(self) -> str:
        return "risk_rule_engine"

    @property
    def description(self) -> str:
        return (
            "Evaluate applicant against predefined hard rules. "
            "Returns rule violations that require automatic rejection or manual review."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "age": {"type": "integer", "description": "Applicant age"},
                "income": {"type": "number", "description": "Annual income"},
                "debt_to_income_ratio": {"type": "number", "description": "Debt to income ratio (0-1)"},
                "credit_history_length": {"type": "integer", "description": "Credit history length in years"},
                "existing_loans": {"type": "integer", "description": "Number of existing loans"},
                "loan_amount": {"type": "number", "description": "Requested loan amount"},
            },
            "required": ["age", "income", "debt_to_income_ratio"],
        }

    async def execute(self, **kwargs) -> ToolResult:
        """Execute rule matching."""
        try:
            violations = []

            # Check each rule
            age = kwargs.get("age", 0)
            income = kwargs.get("income", 0)
            debt_ratio = kwargs.get("debt_to_income_ratio", 0)
            credit_history = kwargs.get("credit_history_length", 0)

            # Rule 1: Debt ratio
            if debt_ratio > 0.7:
                violations.append({
                    "rule_id": "rule_001",
                    "status": "reject",
                    "reason": f"负债率 {debt_ratio:.1%} 超过70%上限",
                })

            # Rule 2: Age
            if age < 18 or age > 70:
                violations.append({
                    "rule_id": "rule_002",
                    "status": "reject",
                    "reason": f"年龄 {age} 不在允许范围(18-70岁)",
                })

            # Rule 3: Credit history
            if credit_history < 1:
                violations.append({
                    "rule_id": "rule_003",
                    "status": "review",
                    "reason": f"信用记录 {credit_history} 年，需人工复核",
                })

            # Rule 4: Income
            if income < 10000:
                violations.append({
                    "rule_id": "rule_004",
                    "status": "reject",
                    "reason": f"年收入 {income} 低于1万元门槛",
                })

            # Determine final action
            reject_count = sum(1 for v in violations if v["status"] == "reject")
            review_count = sum(1 for v in violations if v["status"] == "review")

            result = {
                "violations": violations,
                "reject_count": reject_count,
                "review_count": review_count,
                "final_action": "reject" if reject_count > 0 else ("review" if review_count > 0 else "pass"),
                "rule_match_count": len(violations),
            }

            return ToolResult(
                success=True,
                content=json.dumps(result, indent=2, ensure_ascii=False),
            )

        except Exception as e:
            return ToolResult(success=False, content="", error=f"Rule engine failed: {str(e)}")
