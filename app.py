"""
信贷评分系统 - Streamlit 前端
基于多智能体协同的风控决策 Dashboard
"""
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# 配置页面
st.set_page_config(
    page_title="信贷评分系统",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 地址
API_BASE_URL = "http://localhost:8000"

# 自定义 CSS - 深色主题
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        min-height: 100vh;
    }
    .card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
    }
    h1, h2, h3 {
        color: #f1f5f9 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
    }
    .stTextInput > div > div, .stNumberInput > div > div {
        background: #ffffff !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
    }
    .stTextInput input, .stTextArea textarea {
        color: #000000 !important;
    }
    .stTextInput input::placeholder {
        color: #6b7280 !important;
    }
    /* 标签文字 - 亮白色 */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stSlider label, .stTextArea label {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
    }
   /* 下拉框整体 */
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #f1f5f9 !important; /* 匹配下方文本框的浅亮背景 */
        border: 1px solid rgba(148, 163, 184, 0.5) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] * {
        color: #0f172a !important; /* 关键：文字必须改成深色才能在亮底上显示 */
    }

    /* 下拉框选项 */
    div[role="listbox"] {
        background-color: #ffffff !important; /* 下拉列表保持纯白背景 */
    }
    div[role="option"] {
        color: #0f172a !important; /* 选项文字改为深色，确保可见 */
    }
    div[role="option"]:hover {
        background-color: #cbd5e1 !important; /* 鼠标悬停时的浅灰色 */
    }olor: #f1f5f9 !important;
    }
    /* 下拉框输入框 */
    .stSelectbox input {
        color: #f1f5f9 !important;
        background: transparent !important;
    }
    /* 下拉框选项 */
    div[data-baseweb="select"] div[role="listbox"] {
        background: #1e293b !important;
    }
    div[data-baseweb="select"] div[role="option"] span,
    div[data-baseweb="select"] div[role="option"],
    div[data-baseweb="select"] div[role="option"] div {
        color: #f1f5f9 !important;
    }
    div[data-baseweb="select"] div[role="option"]:hover {
        background: #3b82f6 !important;
    }
    /* Streamlit expander 文字颜色 */
    .streamlit-expanderHeader {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }
    /* markdown 正文文字 */
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #e2e8f0 !important;
    }
    /* 列表文字 */
    ul li, ol li {
        color: #e2e8f0 !important;
    }
    /* markdown 链接 */
    .stMarkdown a {
        color: #60a5fa !important;
    }
    div[data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95);
    }
    .badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-green { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
    .badge-red { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
    .badge-yellow { background: rgba(234, 179, 8, 0.2); color: #eab308; }
    .agent-card {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid;
    }
    .agent-numeric { border-color: #a855f7; }
    .agent-semantic { border-color: #14b8a6; }
    .agent-supervisor { border-color: #f59e0b; }
</style>
""", unsafe_allow_html=True)


def call_api(endpoint: str, data: dict):
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ 无法连接后端服务，请确保已启动: python -m uvicorn mini_agent.web.api:app --reload")
        return None
    except Exception as e:
        st.error(f"❌ 请求失败: {str(e)}")
        return None


def check_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def render_header():
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 20px;">💰</span>
            </div>
            <div>
                <div style="font-size: 18px; font-weight: 700; color: #f1f5f9;">信贷评分系统</div>
                <div style="font-size: 12px; color: #94a3b8;">基于 LangGraph + MiniMax 多智能体协同</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        is_healthy = check_health()
        status_color = "#22c55e" if is_healthy else "#ef4444"
        status_text = "🟢 系统正常" if is_healthy else "🔴 服务异常"
        st.markdown(f'<div style="background: rgba(30, 41, 59, 0.5); padding: 8px 16px; border-radius: 8px;"><span style="color: {status_color};">{status_text}</span></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div style="background: rgba(30, 41, 59, 0.5); padding: 8px 16px; border-radius: 8px;"><span style="color: #94a3b8;">🤖 MiniMax-M2.5</span></div>', unsafe_allow_html=True)
    with col4:
        current_time = datetime.now().strftime("%H:%M")
        st.markdown(f'<div style="background: rgba(30, 41, 59, 0.5); padding: 8px 16px; border-radius: 8px; text-align: center;"><span style="color: #94a3b8;">🕐 {current_time}</span></div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)


def render_agent_trace(trace: list):
    st.markdown("### 🔄 推理链路")
    agents_status = {
        "numeric": {"name": "数值分析", "icon": "📊", "completed": False},
        "semantic": {"name": "语义审计", "icon": "🔍", "completed": False},
        "supervisor": {"name": "主控决策", "icon": "🎯", "completed": False},
    }
    for step in trace:
        if step.get("agent") in agents_status:
            agents_status[step.get("agent")]["completed"] = True

    for agent_key, agent_info in agents_status.items():
        status_icon = "✅" if agent_info["completed"] else "⏳"
        color = "#a855f7" if agent_key == "numeric" else "#14b8a6" if agent_key == "semantic" else "#f59e0b"
        st.markdown(f"""
        <div class="agent-card" style="border-color: {color};">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #f1f5f9; font-weight: 600;">{agent_info['icon']} {agent_info['name']}</span>
                <span>{status_icon}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 📝 执行日志")
    if not trace:
        st.info("等待评估...")
    else:
        for i, step in enumerate(trace):
            with st.expander(f"步骤 {i+1}: {step.get('action', '系统')[:40]}..."):
                if step.get("action"): st.markdown(f"**操作:** {step['action']}")
                if step.get("result"): st.markdown(f"**结果:** {step['result']}")
                if step.get("error"): st.markdown(f"**错误:** ❌ {step['error']}")
                if step.get("decision"):
                    color = "#22c55e" if step["decision"] == "approve" else "#ef4444" if step["decision"] == "reject" else "#eab308"
                    text = "✅ 批准" if step["decision"] == "approve" else "❌ 拒绝" if step["decision"] == "reject" else "⚠️ 待复核"
                    st.markdown(f"**决策:** <span style='color: {color}; font-weight: bold;'>{text}</span>", unsafe_allow_html=True)


def render_decision_console(result: dict):
    if not result:
        st.markdown("### 📝 信用评估申请")
        with st.form("credit_form"):
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("年龄", 18, 100, 35)
                income = st.number_input("年收入 (¥)", 0, 1000000, 80000, 1000)
                credit_history = st.number_input("信用历史 (年)", 0, 50, 5)
                debt_ratio = st.slider("负债率", 0.0, 1.0, 0.3, 0.01)
            with col2:
                employment = st.number_input("工作年限 (年)", 0, 50, 3)
                loan_amount = st.number_input("贷款金额 (¥)", 0, 500000, 50000, 1000)
                existing_loans = st.number_input("现有贷款数", 0, 20, 1)
                payment_history = st.slider("还款历史", 0.0, 1.0, 0.9, 0.01)

            loan_purpose = st.text_input("贷款用途", "房屋装修")

            st.markdown("#### 📄 文本资料")
            app_statement = st.text_area("贷款申请说明", "贷款用于房屋装修，已签订装修合同，有稳定收入来源。", 3)
            credit_remarks = st.text_area("信用备注（可选）", "信用记录良好，无逾期记录。", 2)

            submitted = st.form_submit_button("🚀 提交评估", type="primary", use_container_width=True)
            if submitted:
                return {
                    "numeric_data": {
                        "age": age, "income": income, "credit_history_length": credit_history,
                        "debt_to_income_ratio": debt_ratio, "employment_length": employment,
                        "loan_amount": loan_amount, "loan_purpose": loan_purpose,
                        "existing_loans": existing_loans, "payment_history": payment_history
                    },
                    "text_data": {"application_statement": app_statement, "credit_remarks": credit_remarks}
                }
        return None

    # 显示结果
    final_decision = result.get("final_decision", "error")
    decision_reason = result.get("decision_reason", "")
    numeric_result = result.get("numeric_result", {})
    credit_score = numeric_result.get("credit_score", 0)
    risk_level = numeric_result.get("risk_level", "medium")
    prob_default = numeric_result.get("probability_default", 0)
    features_importance = numeric_result.get("features_importance", {})

    st.markdown("### 💰 信用评分")

    col1, col2 = st.columns([1, 2])
    with col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=credit_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "信用评分", 'font': {'size': 20, 'color': '#f1f5f9'}},
            number={'font': {'size': 48, 'color': '#f1f5f9'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': "#64748b"},
                'bar': {'color': f"rgba({255 if credit_score < 50 else 234}, {179 if credit_score < 50 else 197}, 8, 0.8)"},
                'bgcolor': "rgba(30, 41, 59, 0.5)",
                'steps': [
                    {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.2)"},
                    {'range': [50, 70], 'color': "rgba(234, 179, 8, 0.2)"},
                    {'range': [70, 100], 'color': "rgba(34, 197, 94, 0.2)"},
                ],
            }
        ))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': '#f1f5f9'}, height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        risk_colors = {"low": ("低风险", "#22c55e"), "medium": ("中等风险", "#eab308"), "high": ("高风险", "#ef4444")}
        risk_text, risk_color = risk_colors.get(risk_level, ("中等风险", "#eab308"))
        badge_class = "badge-green" if final_decision == "approve" else "badge-red" if final_decision == "reject" else "badge-yellow"
        decision_text = "✅ 批准" if final_decision == "approve" else "❌ 拒绝" if final_decision == "reject" else "⚠️ 待复核"

        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 16px; border: 1px solid rgba(148, 163, 184, 0.1);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
                <span style="color: #94a3b8;">违约概率</span>
                <span style="color: #f1f5f9; font-size: 24px; font-weight: 600;">{prob_default*100:.1f}%</span>
            </div>
            <div style="background: #1e293b; border-radius: 8px; height: 12px;">
                <div style="background: linear-gradient(90deg, #22c55e, #eab308, #ef4444); height: 100%; width: {prob_default*100}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 16px;">
                <span style="color: #94a3b8;">风险等级</span>
                <span class="badge" style="background: {risk_color}20; color: {risk_color};">{risk_text}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 12px;">
                <span style="color: #94a3b8;">最终决策</span>
                <span class="badge {badge_class}">{decision_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # SHAP 特征
    st.markdown("### 📈 SHAP 特征贡献")
    if features_importance:
        feature_names = {"age": "年龄", "income": "收入", "credit_history_length": "信用历史", "debt_to_income_ratio": "负债率",
                        "employment_length": "工作年限", "loan_amount": "贷款金额", "existing_loans": "现有贷款", "payment_history": "还款记录"}
        data = [{"feature": feature_names.get(k, k), "importance": v} for k, v in features_importance.items()]
        data.sort(key=lambda x: abs(x["importance"]), reverse=True)
        fig_bar = px.bar(data[:8], x="importance", y="feature", orientation='h', color="importance",
                        color_continuous_scale=["#ef4444", "#eab308", "#22c55e"])
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#f1f5f9'}, height=280, margin=dict(l=80, r=20, t=20, b=40))
        st.plotly_chart(fig_bar, use_container_width=True)

    # 冲突检测
    if result.get("conflict_detected"):
        st.markdown(f"""
        <div style="background: rgba(234, 179, 8, 0.1); border: 1px solid rgba(234, 179, 8, 0.3); padding: 16px; border-radius: 12px;">
            <span style="color: #eab308; font-weight: 600;">⚠️ 冲突检测: </span>
            <span style="color: #94a3b8;">{result.get('conflict_details', '数值与语义分析存在冲突')}</span>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 重新评估", use_container_width=True):
        st.session_state.result = None
        st.rerun()

    return None


def render_ai_report(result: dict):
    if not result:
        st.markdown("### 🤖 AI 准入建议")
        st.info("提交评估后显示分析建议")
        st.markdown("### 📋 合规报告")
        st.info("暂无报告")
        return

    final_decision = result.get("final_decision", "error")
    decision_reason = result.get("decision_reason", "")
    semantic_risk = result.get("semantic_risk", {})
    credit_report = result.get("credit_report", {})

    decision_color = "#22c55e" if final_decision == "approve" else "#ef4444" if final_decision == "reject" else "#eab308"
    decision_text = "建议批准" if final_decision == "approve" else "建议拒绝" if final_decision == "reject" else "建议人工复核"

    st.markdown("### 🤖 AI 准入建议")
    st.markdown(f"""
    <div style="background: {decision_color}10; border: 1px solid {decision_color}30; padding: 20px; border-radius: 16px; margin-bottom: 20px;">
        <div style="font-size: 20px; font-weight: 700; color: {decision_color}; margin-bottom: 12px;">{decision_text}</div>
        <p style="color: #f1f5f9; font-size: 14px;">{decision_reason}</p>
    </div>
    """, unsafe_allow_html=True)

    if semantic_risk:
        st.markdown("#### 🔍 语义分析")
        col1, col2 = st.columns(2)
        willingness = semantic_risk.get("repayment_willingness", "medium")
        industry_risk = semantic_risk.get("industry_risk", "low")
        will_color = "#22c55e" if willingness == "high" else "#eab308" if willingness == "medium" else "#ef4444"
        risk_color = "#22c55e" if industry_risk == "low" else "#eab308" if industry_risk == "medium" else "#ef4444"
        with col1:
            st.markdown(f'<div style="background: rgba(30,41,59,0.5); padding: 16px; border-radius: 12px;"><div style="color:#94a3b8; font-size:12px;">还款意愿</div><span class="badge" style="background:{will_color}20; color:{will_color};">{"高" if willingness=="high" else "中" if willingness=="medium" else "低"}</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="background: rgba(30,41,59,0.5); padding: 16px; border-radius: 12px;"><div style="color:#94a3b8; font-size:12px;">行业风险</div><span class="badge" style="background:{risk_color}20; color:{risk_color};">{"低" if industry_risk=="low" else "中" if industry_risk=="medium" else "高"}</span></div>', unsafe_allow_html=True)

        if semantic_risk.get("concerns"):
            st.markdown("##### ⚠️ 关注点")
            for c in semantic_risk["concerns"]: st.markdown(f"- {c}")
        if semantic_risk.get("fraud_indicators"):
            st.markdown("##### 🔴 风险警示")
            for f in semantic_risk["fraud_indicators"]: st.markdown(f"- {f}")

    # 雷达图
    st.markdown("### 📊 五维能力评估")
    if result.get("numeric_result") and semantic_risk:
        radar_data = [
            {"metric": "还款能力", "value": {"high": 85, "medium": 60, "low": 35}.get(semantic_risk.get("repayment_willingness", "medium"), 50)},
            {"metric": "信用历史", "value": 70},
            {"metric": "收入稳定", "value": 75},
            {"metric": "负债水平", "value": 80},
            {"metric": "资产储备", "value": 65},
        ]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=[d["value"] for d in radar_data], theta=[d["metric"] for d in radar_data],
            fill='toself', fillcolor='rgba(59, 130, 246, 0.3)', line=dict(color='#22d3ee', width=2)))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickcolor="#64748b", gridcolor="rgba(148,163,184,0.1)")),
            paper_bgcolor='rgba(0,0,0,0)', font={'color': '#f1f5f9'}, showlegend=False, height=350, margin=dict(l=40, r=40, t=20, b=20))
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("暂无数据")

    st.markdown("### 📋 完整评估报告")
    if credit_report:
        # 决策结果 - 突出显示
        decision = credit_report.get("final_decision", "")
        decision_color = "#22c55e" if decision == "approve" else "#ef4444" if decision == "reject" else "#eab308"
        decision_text = "✅ 批准" if decision == "approve" else "❌ 拒绝" if decision == "reject" else "⚠️ 待复核"
        st.markdown(f"""
        <div style="background: {decision_color}15; border: 2px solid {decision_color}; padding: 20px; border-radius: 16px; margin-bottom: 16px; text-align: center;">
            <div style="font-size: 28px; font-weight: 700; color: {decision_color}; margin-bottom: 8px;">{decision_text}</div>
            <div style="color: #f1f5f9; font-size: 14px;">{credit_report.get('decision_reason', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        # 报告基本信息
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.5); padding: 16px; border-radius: 12px; margin-bottom: 16px;">
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
                <div><span style="color: #94a3b8;">报告编号</span><br><span style="color: #f1f5f9; font-family: monospace;">{credit_report.get('report_id', 'N/A')}</span></div>
                <div><span style="color: #94a3b8;">评估时间</span><br><span style="color: #f1f5f9;">{credit_report.get('evaluation_time', 'N/A')}</span></div>
                <div><span style="color: #94a3b8;">综合评分</span><br><span style="color: #22c55e; font-weight: bold; font-size: 18px;">{credit_report.get('overall_score', 'N/A')}</span></div>
                <div><span style="color: #94a3b8;">风险等级</span><br>
                    <span class="{'badge-green' if credit_report.get('risk_level') == 'low' else 'badge-yellow' if credit_report.get('risk_level') == 'medium' else 'badge-red'}">
                        {'低' if credit_report.get('risk_level') == 'low' else '中' if credit_report.get('risk_level') == 'medium' else '高'}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 申请人信息
        applicant = credit_report.get("applicant_info", {})
        if applicant:
            with st.expander("📄 申请人信息", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    - **年龄**: {applicant.get('age', 'N/A')}
                    - **年收入**: ¥{applicant.get('income', 'N/A'):,}
                    - **贷款用途**: {applicant.get('loan_purpose', 'N/A')}
                    - **贷款金额**: ¥{applicant.get('loan_amount', 'N/A'):,}
                    - **负债率**: {applicant.get('debt_to_income_ratio', 'N/A')}
                    - **贷款/收入比**: {applicant.get('loan_to_income_ratio', 'N/A')}倍
                    """)
                with col2:
                    st.markdown(f"""
                    - **信用历史**: {applicant.get('credit_history_length', 'N/A')}年
                    - **工作年限**: {applicant.get('employment_length', 'N/A')}年
                    - **现有贷款**: {applicant.get('existing_loans', 'N/A')}笔
                    - **还款历史**: {applicant.get('payment_history', 'N/A')}
                    """)
                # 文本资料
                if applicant.get('application_statement'):
                    st.markdown("---")
                    st.markdown("**贷款申请说明:**")
                    st.markdown(f"_{applicant.get('application_statement', '')}_")
                if applicant.get('credit_remarks') and applicant.get('credit_remarks') != 'N/A':
                    st.markdown(f"**信用备注:** {applicant.get('credit_remarks', '')}")

        # 数值分析
        numeric = credit_report.get("numeric_analysis", {})
        if numeric:
            with st.expander("📊 数值分析结果", expanded=True):
                st.markdown(f"""
                - **信用评分**: {numeric.get('credit_score', 'N/A')}
                - **违约概率**: {numeric.get('probability_default', 'N/A'):.2%}
                - **风险等级**: {numeric.get('risk_level', 'N/A')}
                """)
                # SHAP 特征重要性
                features = numeric.get("features_importance", {})
                if features:
                    st.markdown("**SHAP 特征贡献:**")
                    feature_names = {"age": "年龄", "income": "收入", "credit_history_length": "信用历史",
                                   "debt_to_income_ratio": "负债率", "employment_length": "工作年限",
                                   "loan_amount": "贷款金额", "existing_loans": "现有贷款", "payment_history": "还款记录"}
                    items = [(feature_names.get(k, k), v) for k, v in features.items()]
                    items.sort(key=lambda x: abs(x[1]), reverse=True)
                    for name, val in items[:6]:
                        st.markdown(f"  - {name}: {val:.4f}")

        # 语义分析
        semantic = credit_report.get("semantic_analysis", {})
        if semantic:
            with st.expander("🔍 语义分析结果", expanded=True):
                st.markdown(f"""
                - **还款意愿**: {'高' if semantic.get('repayment_willingness') == 'high' else '中' if semantic.get('repayment_willingness') == 'medium' else '低'}
                - **行业风险**: {'低' if semantic.get('industry_risk') == 'low' else '中' if semantic.get('industry_risk') == 'medium' else '高'}
                """)
                if semantic.get("fraud_indicators"):
                    st.markdown("**🚨 欺诈指标:**")
                    for item in semantic["fraud_indicators"]:
                        st.markdown(f"  - {item}")
                if semantic.get("concerns"):
                    st.markdown("**⚠️ 关注点:**")
                    for item in semantic["concerns"]:
                        st.markdown(f"  - {item}")

        # 规则检查
        rules = credit_report.get("rule_results", {})
        if rules:
            with st.expander("✅ 风控规则检查", expanded=True):
                st.markdown(f"**规则通过**: {'是' if rules.get('passed') else '否'}")
                if rules.get("passed_rules"):
                    st.markdown("**通过规则:**")
                    for r in rules["passed_rules"]:
                        st.markdown(f"  ✅ {r}")
                if rules.get("failed_rules"):
                    st.markdown("**未通过规则:**")
                    for r in rules["failed_rules"]:
                        st.markdown(f"  ❌ {r}")

        # 合规依据
        compliance = credit_report.get("compliance_basis", [])
        if compliance:
            with st.expander("⚖️ 合规依据", expanded=True):
                for i, item in enumerate(compliance, 1):
                    if item:
                        st.markdown(f"{i}. {item}")

        # 风险提示
        warnings = credit_report.get("risk_warnings", [])
        if warnings:
            with st.expander("⚠️ 风险提示", expanded=True):
                for warn in warnings:
                    if "✓" in warn:
                        st.markdown(f'<span style="color: #22c55e;">{warn}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span style="color: #ef4444;">{warn}</span>', unsafe_allow_html=True)
    else:
        st.info("暂无报告")


def main():
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'trace' not in st.session_state:
        st.session_state.trace = []

    render_header()

    col_left, col_right = st.columns([1, 2])

    with col_left:
        render_agent_trace(st.session_state.trace)

    with col_right:
        form_data = render_decision_console(st.session_state.result)
        if form_data:
            with st.spinner("🤖 AI 正在分析，多智能体协同决策中..."):
                result = call_api("/api/credit/evaluate", form_data)
                if result:
                    st.session_state.result = result
                    st.session_state.trace = result.get("trace", [])
                    st.rerun()

        # 报告放在中间面板下方
        if st.session_state.result:
            render_ai_report(st.session_state.result)


if __name__ == "__main__":
    main()