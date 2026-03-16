"""Supervisor (main control) agent for credit scoring.

This agent is responsible for:
1. Task orchestration - deciding which sub-agents to invoke
2. Result aggregation - combining results from sub-agents
3. Conflict detection - identifying numeric vs semantic conflicts
4. Decision making - generating final credit decision
5. Self-reflection - reviewing and improving decisions
"""

import json
from typing import Optional

from ...llm import LLMClient
from ...schema import Message
from ...tools.base import Tool
from ..state import CreditState


class SupervisorAgent:
    """Supervisor agent for multi-agent credit scoring.

    This agent acts as the orchestrator, coordinating sub-agents
    and making final decisions.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        tools: list[Tool],
    ):
        """Initialize supervisor agent.

        Args:
            llm_client: LLM client for reasoning
            tools: List of tools available to this agent
        """
        self.llm = llm_client
        self.tools = {tool.name: tool for tool in tools}

    async def run(self, state: CreditState) -> CreditState:
        """Run supervisor logic.

        Args:
            state: Current workflow state

        Returns:
            Updated state with final decision
        """
        try:
            # Check if all required data is present
            has_numeric = state.get("numeric_result") is not None
            has_semantic = state.get("semantic_risk") is not None

            if not has_numeric and not has_semantic:
                state["final_decision"] = "insufficient_data"
                state["decision_reason"] = "缺乏必要数据，无法进行评估"
                state["trace"].append({
                    "agent": "supervisor",
                    "action": "early_exit",
                    "reason": "No data provided",
                })
                return state

            # Detect conflict between numeric and semantic analysis
            conflict_result = self._detect_conflict(state)

            if conflict_result["conflict"]:
                state["conflict_detected"] = True
                state["conflict_details"] = conflict_result["details"]
                state["trace"].append({
                    "agent": "supervisor",
                    "action": "conflict_detected",
                    "details": conflict_result["details"],
                })
            else:
                state["conflict_detected"] = False

            # Make final decision
            decision = await self._make_decision(state)

            state["final_decision"] = decision["decision"]
            state["decision_reason"] = decision["reason"]
            state["trace"].append({
                "agent": "supervisor",
                "action": "final_decision",
                "decision": decision["decision"],
                "reason": decision["reason"],
            })

        except Exception as e:
            state["errors"].append(f"Supervisor error: {str(e)}")
            state["final_decision"] = "error"
            state["decision_reason"] = f"系统错误: {str(e)}"
            state["trace"].append({
                "agent": "supervisor",
                "action": "error",
                "error": str(e),
            })

        return state

    def _detect_conflict(self, state: CreditState) -> dict:
        """Detect conflict between numeric and semantic analysis."""
        numeric_result = state.get("numeric_result", {})
        semantic_risk = state.get("semantic_risk", {})

        if not numeric_result or not semantic_risk:
            return {"conflict": False, "details": ""}

        # Extract key metrics
        credit_score = numeric_result.get("credit_score", 50)
        risk_level = numeric_result.get("risk_level", "medium")
        repayment_willingness = semantic_risk.get("repayment_willingness", "medium")
        industry_risk = semantic_risk.get("industry_risk", "medium")
        fraud_indicators = semantic_risk.get("fraud_indicators", [])

        conflicts = []

        # High score but low repayment willingness
        if credit_score >= 70 and repayment_willingness == "low":
            conflicts.append(f"数值评分高({credit_score})但语义分析还款意愿低")

        # Low risk numeric but high risk semantic (only trigger if fraud_indicators >= 3)
        if risk_level == "low" and len(fraud_indicators) >= 3:
            conflicts.append(f"数值评分低风险但语义分析发现{len(fraud_indicators)}个欺诈指标")

        # High fraud indicators despite good numeric score
        if credit_score >= 60 and len(fraud_indicators) >= 3:
            conflicts.append(f"存在{len(fraud_indicators)}个欺诈指标")

        return {
            "conflict": len(conflicts) > 0,
            "details": "; ".join(conflicts) if conflicts else "",
        }

    async def _make_decision(self, state: CreditState) -> dict:
        """Make final credit decision."""
        numeric_result = state.get("numeric_result", {})
        semantic_risk = state.get("semantic_risk", {})
        conflict_detected = state.get("conflict_detected", False)

        # Build decision context
        context = self._build_decision_context(state)

        # If conflict detected, use LLM for more sophisticated decision
        if conflict_detected:
            decision = await self._llm_decide_with_conflict(context)
        else:
            # Use rule-based decision
            decision = self._rule_based_decision(numeric_result, semantic_risk)

        return decision

    def _build_decision_context(self, state: CreditState) -> str:
        """Build decision context prompt."""
        numeric = state.get("numeric_result", {})
        semantic = state.get("semantic_risk", {})
        conflict = state.get("conflict_details", "")

        context = "【信贷决策分析】\n\n"

        # Numeric results
        if numeric:
            context += f"【数值分析】\n"
            context += f"- 信用评分: {numeric.get('credit_score', 'N/A')}\n"
            context += f"- 违约概率: {numeric.get('probability_default', 'N/A')}\n"
            context += f"- 风险等级: {numeric.get('risk_level', 'N/A')}\n\n"

        # Semantic results
        if semantic:
            context += f"【语义分析】\n"
            context += f"- 还款意愿: {semantic.get('repayment_willingness', 'N/A')}\n"
            context += f"- 行业风险: {semantic.get('industry_risk', 'N/A')}\n"
            context += f"- 欺诈指标: {semantic.get('fraud_indicators', [])}\n"
            context += f"- 风险关注点: {semantic.get('concerns', [])}\n\n"

        # Conflict
        if conflict:
            context += f"【检测到冲突】\n{conflict}\n\n"

        return context

    async def _llm_decide_with_conflict(self, context: str) -> dict:
        """Use LLM to decide when conflict is detected."""
        try:
            prompt = f"""{context}

请根据以上分析，给出最终信贷决策。

要求：
1. 综合考虑数值评分和语义分析
2. 如果数值评分高（>=80）且欺诈指标不严重（<3个），应倾向于通过
3. 只有当欺诈指标真正严重（>=3个）时才能拒绝
4. 给出清晰的 approve/review/reject 结论
5. 说明决策理由

请以JSON格式返回：
{{
    "decision": "approve/review/reject",
    "reason": "具体决策理由"
}}

只返回JSON，不要其他内容。"""

            messages = [
                Message(
                    role="system",
                    content="你是一个专业的信贷决策专家，负责综合多方信息做出最终决策。",
                ),
                Message(role="user", content=prompt),
            ]

            response = await self.llm.generate(messages=messages)

            # Parse response
            import re

            json_match = re.search(r"\{.*\}", response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            # Fallback
            return {
                "decision": "review",
                "reason": "需要人工复核",
            }
        except Exception as e:
            # If LLM fails, fall back to rule-based decision
            return {
                "decision": "review",
                "reason": f"LLM决策失败，需人工复核: {str(e)}",
            }

    def _rule_based_decision(
        self,
        numeric_result: dict,
        semantic_risk: dict,
    ) -> dict:
        """Rule-based decision when no conflict."""
        # Default: approve
        decision = "approve"
        reasons = []

        # Check numeric score
        credit_score = numeric_result.get("credit_score", 0)
        if credit_score < 50:
            decision = "reject"
            reasons.append(f"数值评分过低({credit_score})")
        elif credit_score < 70:
            decision = "review"
            reasons.append(f"数值评分一般({credit_score})")

        # Check semantic risk
        if semantic_risk:
            if semantic_risk.get("repayment_willingness") == "low":
                if decision == "approve":
                    decision = "review"
                reasons.append("还款意愿较低")

            if semantic_risk.get("industry_risk") == "high":
                decision = "reject"
                reasons.append("行业风险高")

            fraud_count = len(semantic_risk.get("fraud_indicators", []))
            if fraud_count >= 3:
                decision = "reject"
                reasons.append(f"存在{fraud_count}个严重欺诈指标")
            elif fraud_count > 0:
                # 有少量欺诈指标但不是严重级别，降级为 review
                if decision == "approve":
                    decision = "review"
                reasons.append(f"存在{fraud_count}个风险关注点")

        return {
            "decision": decision,
            "reason": "; ".join(reasons) if reasons else "综合评估通过",
        }
