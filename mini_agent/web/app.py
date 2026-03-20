"""
Streamlit Web UI for Credit Scoring Multi-Agent System.

Run with:
    streamlit run mini_agent/web/app.py
"""

import streamlit as st
import json
import requests
from typing import Optional
import graphviz

# Page config
st.set_page_config(
    page_title="信贷评分系统",
    page_icon="💰",
    layout="wide",
)

# API URL (can be configured via environment)
API_URL = "http://localhost:8000"


def create_default_input() -> dict:
    """Create default input data for demo."""
    return {
        "numeric_data": {
            "age": 30,
            "income": 80000,
            "credit_history_length": 5,
            "debt_to_income_ratio": 0.3,
            "employment_length": 3,
            "loan_amount": 50000,
            "loan_purpose": "home_improvement",
            "existing_loans": 1,
            "payment_history": 0.9
        },
        "text_data": {
            "application_statement": "我需要贷款30万元用于房屋装修，已签订装修合同30万元，自有资金10万元，贷款期限3年，有稳定收入。",
            "credit_remarks": "信用良好，无逾期记录"
        }
    }


def render_trace_visualization(trace: list) -> None:
    """Render trace as a flowchart."""
    if not trace:
        st.info("无推理链路数据")
        return

    # Create graphviz diagram
    dot = graphviz.Digraph()
    dot.attr(rankdir="TB")
    dot.attr("node", shape="box", style="rounded,filled", fontname="Microsoft YaHei")

    # Add nodes
    for i, step in enumerate(trace):
        agent = step.get("agent", "unknown")
        action = step.get("action", "unknown")
        node_id = f"step_{i}"
        label = f"{agent}\n{action}"
        dot.node(node_id, label, fillcolor="lightblue" if agent in ["numeric", "semantic"] else "lightyellow")

    # Add edges
    for i in range(len(trace) - 1):
        dot.edge(f"step_{i}", f"step_{i+1}")

    # Render
    st.graphviz_chart(dot)


def render_credit_report(result: dict) -> None:
    """Render structured credit evaluation report."""
    report = result.get("credit_report")
    if not report:
        # Fallback to old display
        render_decision_result_old(result)
        return

    # Report header
    st.subheader("📋 信贷评估风控报告")

    # Report metadata
    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.markdown(f"**🏷️ 报告编号:** {report.get('report_id', 'N/A')}")
    with col_meta2:
        st.markdown(f"**📅 评估时间:** {report.get('evaluation_time', 'N/A')}")

    st.divider()

    # 1. Applicant basic info
    st.markdown("### 📌 一、申请人基本信息")
    applicant = report.get("applicant_info", {})
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("年龄", f"{applicant.get('age', 'N/A')}岁")
    with col2:
        st.metric("年收入", f"¥{applicant.get('income', 0):,}")
    with col3:
        st.metric("负债率", f"{applicant.get('debt_to_income_ratio', 0):.1%}")
    with col4:
        st.metric("贷款金额", f"¥{applicant.get('loan_amount', 0):,}")

    col5, col6, col7 = st.columns(3)
    with col5:
        st.metric("信用历史", f"{applicant.get('credit_history_length', 0)}年")
    with col6:
        st.metric("贷款用途", applicant.get("loan_purpose", "N/A"))
    with col7:
        st.metric("现有贷款数", applicant.get("existing_loans", 0))

    # 收入与贷款匹配分析
    loan_to_income = applicant.get("loan_to_income_ratio", 0)
    if loan_to_income > 0:
        col_loan, col_ratio = st.columns(2)
        with col_loan:
            pass
        with col_ratio:
            if loan_to_income <= 2:
                st.success(f"💚 贷款/收入比: {loan_to_income:.1f}倍 (安全)")
            elif loan_to_income <= 3:
                st.warning(f"💛 贷款/收入比: {loan_to_income:.1f}倍 (略高)")
            else:
                st.error(f"❤️ 贷款/收入比: {loan_to_income:.1f}倍 (过高)")

    st.divider()

    # 2. Numeric analysis
    st.markdown("### 📊 二、数值评分分析")
    numeric = report.get("numeric_analysis", {})
    score = numeric.get("credit_score", 0)
    prob = numeric.get("probability_default", 0)
    risk = numeric.get("risk_level", "unknown")

    col_score1, col_score2 = st.columns([1, 2])
    with col_score1:
        st.metric("信用评分", f"{score}/100")
        st.progress(score / 100)
    with col_score2:
        risk_colors = {"low": "green", "medium": "orange", "high": "red"}
        risk_color = risk_colors.get(risk, "gray")
        st.markdown(f"**风险等级:** :{risk_color}[{risk.upper()}]")
        st.markdown(f"**违约概率:** {prob:.2%}")

    # Features importance
    features = numeric.get("features_importance", {})
    if features:
        st.markdown("**关键特征贡献:**")
        sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)
        for name, importance in sorted_features[:5]:
            bar_width = int(importance * 20)
            bar = "█" * bar_width + "░" * (20 - bar_width)
            st.markdown(f"  {name}: {bar} {importance:.0%}")

    st.divider()

    # 3. Semantic analysis
    st.markdown("### 🔍 三、语义风险评估")
    semantic = report.get("semantic_analysis", {})
    willingness = semantic.get("repayment_willingness", "unknown")
    industry_risk = semantic.get("industry_risk", "unknown")
    fraud = semantic.get("fraud_indicators", [])
    concerns = semantic.get("concerns", [])

    col_sem1, col_sem2 = st.columns(2)
    with col_sem1:
        willingness_colors = {"high": "green", "medium": "orange", "low": "red"}
        st.markdown(f"**还款意愿:** :{willingness_colors.get(willingness, 'gray')}[{willingness.upper()}]")
    with col_sem2:
        st.markdown(f"**行业风险:** :{risk_colors.get(industry_risk, 'gray')}[{industry_risk.upper()}]")

    if fraud:
        st.markdown("**⚠️ 欺诈指标:**")
        for item in fraud:
            st.markdown(f"  - {item}")
    else:
        st.markdown("**✅ 无欺诈指标**")

    if concerns:
        st.markdown("**⚡ 风险关注点:**")
        for item in concerns:
            st.markdown(f"  - {item}")

    st.divider()

    # 4. Rule results
    st.markdown("### ⚖️ 四、规则命中情况")
    rules = report.get("rule_results", {})
    passed_rules = rules.get("passed_rules", [])
    failed_rules = rules.get("failed_rules", [])

    if passed_rules:
        st.markdown("**✅ 通过规则:**")
        for rule in passed_rules:
            st.markdown(f"  - {rule}")
    else:
        st.markdown("**✅ 暂无通过规则记录**")

    if failed_rules:
        st.markdown("**❌ 未通过规则:**")
        for rule in failed_rules:
            st.markdown(f"  - {rule}")
    else:
        st.markdown("**✅ 暂无未通过规则**")

    st.divider()

    # 5. Compliance basis
    st.markdown("### 📜 五、合规依据")
    compliance = report.get("compliance_basis", [])
    if compliance:
        for item in compliance:
            st.markdown(f"  - {item}")
    else:
        st.markdown("暂无合规依据")

    st.divider()

    # 6. Risk warnings
    st.markdown("### ⚠️ 六、风险提示")
    warnings = report.get("risk_warnings", [])
    if warnings:
        for item in warnings:
            if "✓" in item:
                st.success(item)
            else:
                st.warning(item)
    else:
        st.info("暂无风险提示")

    st.divider()

    # 7. Final decision
    decision = report.get("final_decision", "")
    reason = report.get("decision_reason", "")
    overall_score = report.get("overall_score", 0)
    risk_level = report.get("risk_level", "unknown")

    if decision == "approve":
        st.success(f"## ✅ 批准贷款")
    elif decision == "reject":
        st.error(f"## ❌ 拒绝贷款")
    elif decision == "review":
        st.warning(f"## ⚠️ 待复核")
    else:
        st.info(f"## 📋 {decision}")

    st.markdown(f"**综合评分:** {overall_score}分  |  **风险等级:** {risk_level.upper()}")
    st.markdown(f"**决策理由:** {reason}")


def render_decision_result_old(result: dict) -> None:
    """Render decision result with proper styling (fallback)."""
    decision = result.get("final_decision", "").lower()
    reason = result.get("decision_reason", "")
    numeric = result.get("numeric_result", {})
    semantic = result.get("semantic_risk", {})
    conflict = result.get("conflict_detected", False)
    conflict_details = result.get("conflict_details", "")

    # Decision header
    if decision == "approve":
        st.success(f"✅ **通过** - 贷款申请批准")
    elif decision == "reject":
        st.error(f"❌ **拒绝** - 贷款申请被拒绝")
    elif decision == "review":
        st.warning(f"⚠️ **待复核** - 需要人工审核")
    else:
        st.info(f"📋 决策: {decision}")

    # Reason
    if reason:
        st.markdown(f"**决策理由:** {reason}")

    # Columns for details
    col1, col2 = st.columns(2)

    # Numeric analysis
    with col1:
        st.subheader("📊 数值分析")
        if numeric:
            score = numeric.get("credit_score", 0)
            prob = numeric.get("probability_default", 0)
            risk = numeric.get("risk_level", "unknown")

            # Score progress bar
            st.metric("信用评分", f"{score}/100")
            st.progress(score / 100)

            # Risk level with color
            risk_colors = {"low": "green", "medium": "orange", "high": "red"}
            st.markdown(f"**风险等级:** :{risk_colors.get(risk, 'gray')}[{risk.upper()}]")
            st.markdown(f"**违约概率:** {prob:.2%}")
        else:
            st.info("无数值分析数据")

    # Semantic analysis
    with col2:
        st.subheader("🔍 语义分析")
        if semantic:
            willingness = semantic.get("repayment_willingness", "unknown")
            industry_risk = semantic.get("industry_risk", "unknown")
            fraud = semantic.get("fraud_indicators", [])

            st.markdown(f"**还款意愿:** {willingness}")
            st.markdown(f"**行业风险:** {industry_risk}")

            if fraud:
                st.markdown("**⚠️ 欺诈指标:**")
                for item in fraud:
                    st.markdown(f"  - {item}")
            else:
                st.markdown("**✅ 无欺诈指标**")
        else:
            st.info("无语义分析数据")

    # Conflict detection
    if conflict:
        st.warning(f"⚠️ **冲突检测:** {conflict_details}")

    # Trace
    st.subheader("🔗 推理链路")
    trace = result.get("trace", [])
    if trace:
        render_trace_visualization(trace)

        # Also show as list
        with st.expander("查看原始 Trace 数据"):
            st.json(trace)
    else:
        st.info("无推理链路数据")


def main():
    """Main Streamlit app."""
    # Title
    st.title("💰 信贷评分多智能体系统")
    st.markdown("基于 LangGraph + 多智能体协同的风控决策系统")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ 配置")
        api_url = st.text_input("API 地址", API_URL)

        st.divider()

        st.header("ℹ️ 说明")
        st.markdown("""
        **输入格式:**
        - `numeric_data`: 结构化数值特征
        - `text_data`: 非结构化文本

        **决策结果:**
        - ✅ 通过: 批准贷款
        - ❌ 拒绝: 拒绝贷款
        - ⚠️ 待复核: 需要人工审核
        """)

    # Main content
    st.header("📝 输入申请数据")

    # Input method: JSON or Form
    input_method = st.radio("输入方式", ["JSON", "表单"], horizontal=True)

    if input_method == "JSON":
        default_json = json.dumps(create_default_input(), indent=2, ensure_ascii=False)
        json_input = st.text_area(
            "申请数据 (JSON)",
            value=default_json,
            height=300,
            help="请输入符合格式的 JSON 数据"
        )

        try:
            input_data = json.loads(json_input)
            parse_error = None
        except json.JSONDecodeError as e:
            input_data = None
            parse_error = str(e)
            st.error(f"JSON 解析错误: {e}")
    else:
        st.info("表单输入开发中，请使用 JSON 方式")
        input_data = None

    # Evaluate button
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("🚀 开始评估", type="primary", disabled=input_data is None):
            evaluate = True
        else:
            evaluate = False

    with col2:
        if st.button("📋 加载示例数据"):
            st.rerun()

    # Evaluate
    if evaluate and input_data:
        with st.spinner("🔄 评估中，请稍候..."):
            try:
                # Call API
                response = requests.post(
                    f"{api_url}/api/credit/evaluate",
                    json=input_data,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    st.divider()
                    render_credit_report(result)
                else:
                    st.error(f"API 错误: {response.status_code} - {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到 API 服务器，请确保后端服务已启动")
                st.info("💡 提示: 运行 `uvicorn mini_agent.web.api:app --reload` 启动后端")
            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")


if __name__ == "__main__":
    main()
