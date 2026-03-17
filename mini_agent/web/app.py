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


def render_decision_result(result: dict) -> None:
    """Render decision result with proper styling."""
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
                    render_decision_result(result)
                else:
                    st.error(f"API 错误: {response.status_code} - {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ 无法连接到 API 服务器，请确保后端服务已启动")
                st.info("💡 提示: 运行 `uvicorn mini_agent.web.api:app --reload` 启动后端")
            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")


if __name__ == "__main__":
    main()
