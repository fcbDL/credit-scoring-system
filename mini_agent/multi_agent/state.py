"""LangGraph state definition for credit scoring multi-agent system."""

from typing import TypedDict, Optional, Any
from pydantic import BaseModel, Field


class NumericResult(BaseModel):
    """Numeric analysis result from XGBoost model."""

    credit_score: float = Field(description="Credit score from XGBoost (0-100)")
    probability_default: float = Field(description="Probability of default (0-1)")
    risk_level: str = Field(description="Risk level: low/medium/high")
    features_importance: dict[str, float] = Field(default_factory=dict, description="Feature importance scores")


class SemanticRisk(BaseModel):
    """Semantic risk analysis result from text analysis."""

    fraud_indicators: list[str] = Field(default_factory=list, description="Detected fraud indicators")
    repayment_willingness: str = Field(description="Repayment willingness: high/medium/low")
    industry_risk: str = Field(description="Industry risk level: low/medium/high")
    concerns: list[str] = Field(default_factory=list, description="Risk concerns from text analysis")
    confidence: float = Field(description="Confidence score (0-1)")


class CreditReport(BaseModel):
    """Structured credit evaluation report."""

    report_id: str = Field(description="Report unique ID")
    evaluation_time: str = Field(description="Evaluation timestamp")

    # Applicant basic info
    applicant_info: dict[str, Any] = Field(default_factory=dict, description="Applicant basic information")

    # Numeric analysis
    numeric_analysis: dict[str, Any] = Field(default_factory=dict, description="Numeric score analysis")

    # Semantic analysis
    semantic_analysis: dict[str, Any] = Field(default_factory=dict, description="Semantic risk analysis")

    # Rule checking
    rule_results: dict[str, Any] = Field(default_factory=dict, description="Rule check results")

    # Compliance
    compliance_basis: list[str] = Field(default_factory=list, description="Compliance basis from regulations")

    # Risk warnings
    risk_warnings: list[str] = Field(default_factory=list, description="Risk warnings")

    # Final decision
    final_decision: str
    decision_reason: str
    overall_score: int
    risk_level: str


class CreditState(TypedDict):
    """LangGraph state for credit scoring workflow.

    This state is passed between nodes in the LangGraph workflow,
    containing all information needed for decision making.
    """

    # User input
    user_input: str
    user_id: Optional[str]

    # Numeric analysis results
    numeric_data: Optional[dict[str, Any]]
    numeric_result: Optional[NumericResult]

    # Semantic analysis results
    text_data: Optional[dict[str, Any]]
    semantic_risk: Optional[SemanticRisk]

    # Rule checking results
    rule_result: Optional[dict[str, Any]]

    # Conflict handling
    conflict_detected: bool
    conflict_details: Optional[str]
    audit_result: Optional[str]
    audit_iterations: int

    # Final decision
    final_decision: str
    decision_reason: str

    # Structured credit report
    credit_report: Optional[CreditReport]

    # Trace for explainability
    trace: list[dict[str, Any]]
    errors: list[str]
