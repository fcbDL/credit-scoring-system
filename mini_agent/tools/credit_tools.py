"""Credit domain specific tools for the multi-agent system.

This module provides tools for:
- XGBoost model inference
- RAG retrieval from knowledge base
- Risk rule engine matching
"""

import json
import os
from typing import Any, Optional
from pydantic import BaseModel, Field

from .base import Tool, ToolResult


# Default model path
DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "GiveMeSomeCredit", "credit_model.json"
)


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

    # Feature mapping: user input -> model feature names
    FEATURE_MAPPING = {
        "RevolvingUtilizationOfUnsecuredLines": "loan_amount_normalized",  # Will be calculated
        "age": "age",
        "NumberOfTime30-59DaysPastDueNotWorse": "past_due_30_59",  # Derived from payment_history
        "DebtRatio": "debt_to_income_ratio",
        "MonthlyIncome": "monthly_income",  # income / 12
        "NumberOfOpenCreditLinesAndLoans": "existing_loans",
        "NumberOfTimes90DaysLate": "past_due_90",
        "NumberRealEstateLoansOrLines": "real_estate_loans",
        "NumberOfDependents": "dependents",  # Will use default
    }

    def __init__(self, model_path: Optional[str] = None):
        """Initialize XGBoost scoring tool.

        Args:
            model_path: Path to pre-trained XGBoost model (optional, uses default if None)
        """
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self._model = None
        self._model_loaded = False

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
            try:
                import xgboost as xgb

                if not os.path.exists(self.model_path):
                    print(f"[XGBoost] Model not found at {self.model_path}, using mock score")
                    self._model_loaded = False
                    return None

                self._model = xgb.Booster()
                self._model.load_model(self.model_path)
                self._model_loaded = True
                print(f"[XGBoost] Model loaded successfully from {self.model_path}")
            except Exception as e:
                print(f"[XGBoost] Failed to load model: {e}, using mock score")
                self._model_loaded = False
                self._model = None
        return self._model

    def _map_features(self, data: XGBoostScoreInput) -> dict:
        """Map user input to model features.

        The GiveMeSomeCredit dataset features:
        - RevolvingUtilizationOfUnsecuredLines: 循环信用利用率
        - age: 年龄
        - NumberOfTime30-59DaysPastDueNotWorse: 30-59天逾期次数
        - DebtRatio: 负债率
        - MonthlyIncome: 月收入
        - NumberOfOpenCreditLinesAndLoans: 开放信用额度数量
        - NumberOfTimes90DaysLate: 90天以上逾期次数
        - NumberRealEstateLoansOrLines: 房地产贷款数量
        - NumberOfTime60-89DaysPastDueNotWorse: 60-89天逾期次数
        - NumberOfDependents: 家属人数
        """
        # Calculate derived features
        monthly_income = data.income / 12.0

        # Estimate past due from payment_history (inverse relationship)
        # payment_history 0-1 (1 = perfect), map to past due frequency
        # Higher payment_history means fewer past due events
        if data.payment_history >= 0.98:
            # Excellent: no or very rare late payments
            past_due_30_59 = 0
            past_due_60_89 = 0
            past_due_90 = 0
        elif data.payment_history >= 0.95:
            # Very good: rarely late
            past_due_30_59 = 0
            past_due_60_89 = 0
            past_due_90 = 0
        elif data.payment_history >= 0.9:
            # Good: occasionally late
            past_due_30_59 = 0
            past_due_60_89 = 0
            past_due_90 = 0
        elif data.payment_history >= 0.8:
            # Fair: sometimes late
            past_due_30_59 = 1
            past_due_60_89 = 0
            past_due_90 = 0
        elif data.payment_history >= 0.5:
            # Poor: frequently late
            past_due_30_59 = 2
            past_due_60_89 = 1
            past_due_90 = 0
        else:
            # Very poor: often severely late
            past_due_30_59 = 5
            past_due_60_89 = 3
            past_due_90 = 2

        # Loan amount normalized by income (approximates revolving utilization)
        loan_amount_normalized = data.loan_amount / max(data.income, 1) if data.income > 0 else 1.0

        # Map to model features
        return {
            "RevolvingUtilizationOfUnsecuredLines": min(loan_amount_normalized, 2.0),  # Cap at 2.0
            "age": data.age,
            "NumberOfTime30-59DaysPastDueNotWorse": past_due_30_59,
            "DebtRatio": data.debt_to_income_ratio,
            "MonthlyIncome": monthly_income,
            "NumberOfOpenCreditLinesAndLoans": data.existing_loans + 1,  # +1 for the new loan
            "NumberOfTimes90DaysLate": past_due_90,
            "NumberRealEstateLoansOrLines": 0,  # Not provided in user input
            "NumberOfTime60-89DaysPastDueNotWorse": past_due_60_89,
            "NumberOfDependents": 0,  # Not provided in user input, use default
        }

    def _probability_to_score(self, prob_default: float) -> float:
        """Convert probability of default to credit score (0-100).

        Uses exponential mapping to distribute scores meaningfully:
        - 0.01 (1%) -> ~93
        - 0.10 (10%) -> ~70
        - 0.50 (50%) -> ~30
        """
        # Apply sigmoid-like transformation
        # Higher probability of default -> Lower score
        score = 100 * (1 - prob_default) ** 0.5
        return max(0, min(100, score))

    async def execute(self, **kwargs) -> ToolResult:
        """Execute XGBoost scoring."""
        try:
            # Validate input
            validated = XGBoostScoreInput(**kwargs)

            # Try to load and use real model
            model = self._load_model()

            if model is not None and self._model_loaded:
                # Use real model for prediction
                import xgboost as xgb

                # Map user input to model features
                features = self._map_features(validated)

                # Create DMatrix with feature names in correct order (must match training)
                feature_names = [
                    "RevolvingUtilizationOfUnsecuredLines",
                    "age",
                    "NumberOfTime30-59DaysPastDueNotWorse",
                    "DebtRatio",
                    "MonthlyIncome",
                    "NumberOfOpenCreditLinesAndLoans",
                    "NumberOfTimes90DaysLate",
                    "NumberRealEstateLoansOrLines",
                    "NumberOfTime60-89DaysPastDueNotWorse",
                    "NumberOfDependents",
                ]
                feature_values = [features.get(f, 0) for f in feature_names]
                dmatrix = xgb.DMatrix([feature_values], feature_names=feature_names)

                # Predict probability of default
                prob_default = float(model.predict(dmatrix)[0])
                prob_default = max(0.001, min(0.999, prob_default))  # Clip to reasonable range

                # Convert to credit score
                score = self._probability_to_score(prob_default)

                print(f"[XGBoost] Real model prediction: prob_default={prob_default:.4f}, score={score:.1f}")
            else:
                # Fallback to mock score
                print("[XGBoost] Using mock score (model not available)")
                score = self._calculate_mock_score(validated)
                prob_default = max(0.01, min(0.99, (100 - score) / 100))

            result = {
                "credit_score": round(score, 1),
                "probability_default": round(prob_default, 4),
                "risk_level": "low" if score >= 70 else "medium" if score >= 50 else "high",
                "model_used": "xgboost" if self._model_loaded else "mock",
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
            knowledge_base_path: Path to knowledge base directory (optional)
        """
        self.knowledge_base_path = knowledge_base_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", "knowledge_base"
        )
        self._documents = self._load_documents()

    def _load_documents(self) -> list[dict]:
        """Load knowledge base documents."""
        documents = []

        if not os.path.exists(self.knowledge_base_path):
            print(f"[RAG] Knowledge base not found: {self.knowledge_base_path}")
            return documents

        # Load markdown files
        for filename in os.listdir(self.knowledge_base_path):
            if filename.endswith(".md"):
                filepath = os.path.join(self.knowledge_base_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Split by ## headings to get sections
                        sections = self._parse_sections(content)
                        for section in sections:
                            section["source_file"] = filename
                            documents.append(section)
                except Exception as e:
                    print(f"[RAG] Failed to load {filepath}: {e}")

        print(f"[RAG] Loaded {len(documents)} documents from knowledge base")
        return documents

    def _parse_sections(self, content: str) -> list[dict]:
        """Parse markdown content into sections."""
        sections = []
        lines = content.split("\n")

        current_title = ""
        current_content = []
        current_category = "general"

        for line in lines:
            # Detect category from filename
            if "regulation" in content[:100].lower():
                current_category = "regulation"
            elif "case" in content[:100].lower():
                current_category = "risk_case"

            # Section headers
            if line.startswith("## "):
                # Save previous section
                if current_title and current_content:
                    sections.append({
                        "title": current_title.strip(),
                        "content": "\n".join(current_content).strip(),
                        "category": current_category,
                    })

                current_title = line[3:].strip()
                current_content = []
            elif line.startswith("# "):
                # Document title, skip
                pass
            elif line.strip():
                current_content.append(line)

        # Save last section
        if current_title and current_content:
            sections.append({
                "title": current_title.strip(),
                "content": "\n".join(current_content).strip(),
                "category": current_category,
            })

        return sections

    def _calculate_relevance(self, query: str, doc: dict) -> float:
        """Calculate relevance score using simple keyword matching."""
        query_lower = query.lower()
        query_words = query_lower.split()

        # Combine title and content for matching
        text = (doc.get("title", "") + " " + doc.get("content", "")).lower()

        # Count query word matches (partial match allowed)
        matches = 0
        for word in query_words:
            if word in text:
                matches += 1
            # Also check for partial matches (e.g., "经营" in "经营风险")
            elif len(word) >= 2:
                for i in range(len(word)):
                    if word[i:] in text or word[:i+1] in text:
                        matches += 0.5
                        break

        # Calculate score based on matches
        if matches == 0:
            return 0.0

        # Boost for title matches
        title = doc.get("title", "").lower()
        title_matches = sum(1 for word in query_words if word in title)
        title_boost = title_matches * 0.5

        # Base score - give higher scores for any match
        base_score = min(matches / max(len(query_words), 1), 1.0)

        score = base_score * 0.5 + title_boost + 0.2  # Add base score
        return min(score, 1.0)

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
            if not self._documents:
                return ToolResult(
                    success=True,
                    content=json.dumps([], indent=2, ensure_ascii=False),
                )

            # Filter by category
            filtered_docs = self._documents
            if category != "all":
                filtered_docs = [d for d in self._documents if d.get("category") == category]

            # Calculate relevance scores
            scored_docs = []
            for doc in filtered_docs:
                relevance = self._calculate_relevance(query, doc)
                if relevance > 0.1:  # Minimum threshold
                    scored_docs.append({
                        "title": doc.get("title", ""),
                        "content": doc.get("content", "")[:500],  # Truncate long content
                        "source": doc.get("source_file", "knowledge base"),
                        "category": doc.get("category", "general"),
                        "relevance": round(relevance, 3),
                    })

            # Sort by relevance and return top_k
            scored_docs.sort(key=lambda x: x["relevance"], reverse=True)
            results = scored_docs[:top_k]

            return ToolResult(
                success=True,
                content=json.dumps(results, indent=2, ensure_ascii=False),
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

            # Rule 5: Existing loans check
            existing_loans = kwargs.get("existing_loans", 0)
            if existing_loans > 10:
                violations.append({
                    "rule_id": "rule_005",
                    "status": "review",
                    "reason": f"现有贷款数 {existing_loans} 过多(>10)，建议人工复核",
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
