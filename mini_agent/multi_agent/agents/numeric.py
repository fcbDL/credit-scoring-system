"""Numeric analysis agent for credit scoring.

This agent is responsible for calling XGBoost model and rule engine
to obtain numerical credit assessment.
"""

import json
from typing import Optional

from ...llm import LLMClient
from ...tools.base import Tool
from ...tools.credit_tools import XGBoostScoreTool, RiskRuleEngineTool
from ..state import CreditState, NumericResult


class NumericAgent:
    """Agent for numeric credit analysis.

    This agent:
    1. Runs XGBoost model to get credit score
    2. Checks hard rules (risk rule engine)
    3. Returns structured numeric results
    """

    def __init__(
        self,
        llm_client: LLMClient,
        tools: list[Tool],
    ):
        """Initialize numeric agent.

        Args:
            llm_client: LLM client for potential LLM calls
            tools: List of tools available to this agent
        """
        self.llm = llm_client
        self.tools = {tool.name: tool for tool in tools}

    async def run(self, state: CreditState) -> CreditState:
        """Run numeric analysis.

        Args:
            state: Current workflow state

        Returns:
            Updated state with numeric analysis results
        """
        # Extract numeric data from state
        numeric_data = state.get("numeric_data", {})

        if not numeric_data:
            state["trace"].append({
                "agent": "numeric",
                "action": "skip",
                "reason": "No numeric data provided",
            })
            return state

        try:
            # Run XGBoost scoring
            xgboost_tool = self.tools.get("xgboost_credit_score")
            if xgboost_tool:
                result = await xgboost_tool.execute(**numeric_data)

                if result.success:
                    score_data = json.loads(result.content)
                    numeric_result = NumericResult(
                        credit_score=score_data.get("credit_score", 0),
                        probability_default=score_data.get("probability_default", 0.5),
                        risk_level=score_data.get("risk_level", "unknown"),
                        features_importance=score_data.get("features_importance", {}),
                    )
                    state["numeric_result"] = numeric_result.model_dump()
                    state["trace"].append({
                        "agent": "numeric",
                        "action": "xgboost_score",
                        "result": f"Credit score: {numeric_result.credit_score}, Risk: {numeric_result.risk_level}",
                    })
                else:
                    state["errors"].append(f"XGBoost error: {result.error}")
                    state["trace"].append({
                        "agent": "numeric",
                        "action": "xgboost_error",
                        "error": result.error,
                    })
            else:
                state["errors"].append("XGBoost tool not available")

            # Run rule engine
            rule_tool = self.tools.get("risk_rule_engine")
            if rule_tool:
                result = await rule_tool.execute(**numeric_data)

                if result.success:
                    rule_data = json.loads(result.content)
                    violations = rule_data.get("violations", [])

                    # Calculate passed rules (all rule names minus failed ones)
                    failed_rule_ids = {v.get("rule_id") for v in violations if v.get("rule_id")}
                    all_rule_names = [
                        "负债率上限", "年龄范围", "信用记录要求", "收入要求"
                    ]
                    passed_rule_names = [r for r in all_rule_names if r not in failed_rule_ids]

                    # Store rule result in state
                    state["rule_result"] = {
                        "passed": rule_data.get("final_action") == "pass",
                        "failed_rules": [v.get("description", "") for v in violations],
                        "passed_rules": passed_rule_names,
                    }
                    state["trace"].append({
                        "agent": "numeric",
                        "action": "rule_check",
                        "result": f"Rules matched: {rule_data.get('rule_match_count', 0)}, Action: {rule_data.get('final_action', 'unknown')}",
                        "violations": rule_data.get("violations", []),
                    })
                else:
                    state["errors"].append(f"Rule engine error: {result.error}")

        except Exception as e:
            state["errors"].append(f"Numeric agent error: {str(e)}")
            state["trace"].append({
                "agent": "numeric",
                "action": "error",
                "error": str(e),
            })

        return state
