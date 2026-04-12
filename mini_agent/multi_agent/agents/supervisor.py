"""Supervisor (main control) agent for credit scoring.

This agent is responsible for:
1. Task orchestration - deciding which sub-agents to invoke
2. Result aggregation - combining results from sub-agents
3. Conflict detection - identifying numeric vs semantic conflicts
4. Decision making - generating final credit decision
5. Report generation - creating structured credit evaluation report
"""

import json
import uuid
from datetime import datetime
from typing import Optional

from ...llm import LLMClient
from ...schema import Message
from ...tools.base import Tool
from ..state import CreditState, CreditReport


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

            # Generate structured credit report
            report = self._generate_credit_report(state)
            state["credit_report"] = report

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
        credit_score = (numeric_result or {}).get("credit_score", 0)
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

    def _generate_credit_report(self, state: CreditState) -> CreditReport:
        """Generate structured credit evaluation report."""
        numeric_data = state.get("numeric_data", {})
        numeric_result = state.get("numeric_result", {})
        text_data = state.get("text_data", {})
        semantic_risk = state.get("semantic_risk", {})
        rule_result = state.get("rule_result", {})
        conflict_detected = state.get("conflict_detected", False)
        conflict_details = state.get("conflict_details", "")
        final_decision = state.get("final_decision", "")
        decision_reason = state.get("decision_reason", "")

        # 贷款用途中文映射
        loan_purpose_map = {
            "personal": "个人消费",
            "business": "商业经营",
            "education": "教育培训",
            "home_improvement": "房屋装修",
            "home": "购房",
            "car": "购车",
            "medical": "医疗",
        }
        loan_purpose = numeric_data.get("loan_purpose", "N/A")
        loan_purpose_cn = loan_purpose_map.get(loan_purpose, loan_purpose)

        # 收入与贷款匹配分析
        income = numeric_data.get("income", 0)
        loan_amount = numeric_data.get("loan_amount", 0)
        loan_to_income_ratio = loan_amount / income if income > 0 else 0

        # 1. Applicant basic info
        applicant_info = {
            "age": numeric_data.get("age", "N/A"),
            "income": numeric_data.get("income", "N/A"),
            "credit_history_length": numeric_data.get("credit_history_length", "N/A"),
            "debt_to_income_ratio": numeric_data.get("debt_to_income_ratio", "N/A"),
            "employment_length": numeric_data.get("employment_length", "N/A"),
            "loan_amount": numeric_data.get("loan_amount", "N/A"),
            "loan_purpose": loan_purpose_cn,
            "existing_loans": numeric_data.get("existing_loans", "N/A"),
            "payment_history": numeric_data.get("payment_history", "N/A"),
            "application_statement": text_data.get("application_statement", "N/A"),
            "credit_remarks": text_data.get("credit_remarks", "N/A"),
            "loan_to_income_ratio": round(loan_to_income_ratio, 2),
        }

        # 2. Numeric analysis
        numeric_analysis = {
            "credit_score": numeric_result.get("credit_score", 0),
            "probability_default": numeric_result.get("probability_default", 0),
            "risk_level": numeric_result.get("risk_level", "unknown"),
            "features_importance": numeric_result.get("features_importance", {}),
        }

        # 3. Semantic analysis (handle None)
        semantic_risk_safe = semantic_risk or {}
        semantic_analysis = {
            "repayment_willingness": semantic_risk_safe.get("repayment_willingness", "unknown"),
            "industry_risk": semantic_risk_safe.get("industry_risk", "unknown"),
            "fraud_indicators": semantic_risk_safe.get("fraud_indicators", []),
            "concerns": semantic_risk_safe.get("concerns", []),
        }

        # 4. Rule results
        rule_results = {
            "passed": rule_result.get("passed", True),
            "failed_rules": rule_result.get("failed_rules", []),
            "passed_rules": rule_result.get("passed_rules", []),
        }

        # 5. Compliance basis
        compliance_basis = []

        # 收入与贷款匹配分析
        loan_match_analysis = ""
        if loan_to_income_ratio > 0:
            if loan_to_income_ratio <= 2:
                loan_match_analysis = f"贷款金额/年收入 = {loan_to_income_ratio:.1f}倍，在安全范围内(≤2倍)"
            elif loan_to_income_ratio <= 3:
                loan_match_analysis = f"贷款金额/年收入 = {loan_to_income_ratio:.1f}倍，略高但可接受(2-3倍)"
            else:
                loan_match_analysis = f"贷款金额/年收入 = {loan_to_income_ratio:.1f}倍，超过合理范围(>3倍)"

        if final_decision == "approve":
            compliance_basis.extend([
                "根据《个人贷款管理暂行办法》第七条：贷款人应对借款人提交的材料进行审慎审查，申请人材料齐全，审查通过",
                "根据《商业银行授信工作尽职指引》：应对借款人还款能力进行综合评估，收入稳定，还款能力充足",
                "数值评分良好，信用风险可控",
                loan_match_analysis,
            ])
            if not conflict_detected:
                compliance_basis.append("数值分析与语义分析结论一致，综合评估通过")
        elif final_decision == "reject":
            compliance_basis.extend([
                "根据《个人贷款管理暂行办法》：对不符合贷款条件的申请人应拒绝其申请",
            ])
            if len(semantic_risk_safe.get("fraud_indicators", [])) >= 3:
                compliance_basis.append("语义分析检测到多个欺诈指标，存在重大信贷风险")
            if loan_to_income_ratio > 3:
                compliance_basis.append(loan_match_analysis)
        else:  # review
            compliance_basis.extend([
                "根据《商业银行授信工作尽职指引》：对存在疑问的申请应进行进一步核实",
                "建议补充材料后重新评估",
            ])
            if loan_to_income_ratio > 3:
                compliance_basis.append(loan_match_analysis)

        # 6. Risk warnings
        risk_warnings = []
        if conflict_detected:
            risk_warnings.append(f"⚠️ 数值评分与语义分析存在冲突: {conflict_details}")
        risk_warnings.extend(semantic_risk_safe.get("fraud_indicators", []))
        risk_warnings.extend(semantic_risk_safe.get("concerns", []))
        if not risk_warnings:
            risk_warnings.append("✓ 本次申请未检测到显著风险点")

        # 7. Overall score and risk level
        overall_score = int(numeric_result.get("credit_score", 0))
        risk_level = numeric_result.get("risk_level", "medium")

        report = CreditReport(
            report_id=str(uuid.uuid4())[:8].upper(),
            evaluation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            applicant_info=applicant_info,
            numeric_analysis=numeric_analysis,
            semantic_analysis=semantic_analysis,
            rule_results=rule_results,
            compliance_basis=compliance_basis,
            risk_warnings=risk_warnings,
            final_decision=final_decision,
            decision_reason=decision_reason,
            overall_score=overall_score,
            risk_level=risk_level,
        )

        # Convert to dict for API response
        return report.model_dump()
