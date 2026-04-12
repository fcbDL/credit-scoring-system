# 🤖 基于 LangGraph + LLM 的多智能体协同风控决策系统

<div align="center">

<p>

<img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=fff" alt="Python">
<img src="https://img.shields.io/badge/LangGraph-0.2+-orange?style=for-the-badge" alt="LangGraph">
<img src="https://img.shields.io/badge/XGBoost-AUC%200.85-green?style=for-the-badge" alt="XGBoost">
<img src="https://img.shields.io/badge/FastAPI-0.100+-cyan?style=for-the-badge&logo=fastapi" alt="FastAPI">
<img src="https://img.shields.io/badge/Streamlit-1.40+-red?style=for-the-badge&logo=streamlit&logoColor=fff" alt="Streamlit">

</p>

<h3>基于 LangGraph 状态机的多智能体协同信贷风控决策系统</h3>

</div>

---

## 📖 项目介绍

本系统是一个**智能信贷风险评估平台**，采用 LangGraph 状态机架构，实现多智能体协同决策。

### 🎯 核心功能

| 功能 | 说明 |
|------|------|
| 📊 **智能评分** | 基于 XGBoost 模型自动计算信用评分和违约概率 |
| 🔍 **风险识别** | 利用 LLM 对申请人文本进行语义分析，识别潜在风险 |
| ⚖️ **规则引擎** | 内置风控规则，自动拦截高风险申请 |
| 📚 **知识增强** | RAG 检索信贷法规和风险案例，辅助决策 |
| 🔄 **冲突处理** | 数值与语义分析结果冲突时自动触发二次审计 |

### 🎬 适用场景

- **银行信贷审批** - 个人贷款、信用贷款自动评估
- **消费金融** - 消费分期、信用卡申请风控
- **小微企业贷** - 企业经营贷风险评估
- **助贷平台** - 贷款超市、信贷超市智能风控

### 🏆 核心优势

1. **多维度评估** - 结合数值模型（XGBoost）和语义分析（LLM），避免单一模型偏差
2. **可解释性** - 输出结构化评估报告，包含决策依据和合规引用
3. **可扩展性** - 模块化设计，支持快速接入新规则和新模型
4. **开箱即用** - 提供 Streamlit 前端和 FastAPI 接口，快速部署体验

---

## 🌟 系统亮点

| 特性 | 说明 |
|------|------|
| 🧠 **多智能体协同** | NumericAgent + SemanticAgent + SupervisorAgent 三 Agent 协作 |
| 📊 **XGBoost 评分** | 基于 GiveMeSomeCredit 数据集，AUC 达 0.85 |
| 🔍 **语义分析** | LLM + RAG 知识库增强风险识别 |
| ⚡ **冲突检测** | 数值与语义结果冲突时自动二次审计 |
| 📚 **知识增强** | 信贷法规 + 风险案例检索 |

---

## 🏗️ 技术架构

```
                    ┌─────────────────────┐
                    │   Streamlit 前端    │
                    │  localhost:8501    │
                    └──────────┬──────────┘
                               │ HTTP
                    ┌──────────▼──────────┐
                    │    FastAPI 后端      │
                    │  localhost:8000       │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  LangGraph 状态机   │
                    │  START → agents   │
                    └──────────┬──────────┘
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
      │ XGBoostScore│ │RAGRetrieval│ │ RiskRule   │
      │   数值评分   │ │   知识检索  │ │   规则匹配  │
      └─────────────┘ └─────────────┘ └─────────────┘
```

### Agent 分工

| Agent | 功能 | 输入 | 输出 |
|-------|------|------|------|
| 🤖 **NumericAgent** | XGBoost 评分 + 规则引擎 | numeric_data | credit_score, probability_default, risk_level |
| 🔍 **SemanticAgent** | LLM 语义分析 + RAG 知识增强 | text_data | fraud_indicators, repayment_willingness, industry_risk |
| 🎯 **SupervisorAgent** | 综合决策 + 冲突处理 | numeric_result + semantic_risk | final_decision, decision_reason, credit_report |

### 🔄 工作流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Supervisor │───▶│  Numeric   │───▶│  Semantic  │───▶│  Decision  │
│  调度中心   │    │   Agent    │    │   Agent    │    │   最终决策  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                │                  │
       ▼                  ▼                ▼                  ▼
  任务分配           XGBoost评分       LLM语义分析        决策理由
  冲突检测           规则引擎          RAG知识检索        评估报告
```

---

## 🛠️ 技术栈

### 核心依赖

| 类别 | 技术 | 版本 |
|------|------|------|
| 🤖 Agent 框架 | LangGraph | ≥ 0.2 |
| 🧠 大语言模型 | OpenAI / MiniMax / Claude | - |
| 📈 数值模型 | XGBoost | ≥ 2.0 |
| 🌐 后端 | FastAPI | ≥ 0.100 |
| 🎨 前端 | Streamlit | ≥ 1.40 |
| 💾 数据库 | SQLite (aiosqlite) | - |

### 关键特性

- **状态管理** - LangGraph TypedDict 管理工作流状态
- **错误重试** - Tenacity 实现 LLM 调用自动重试
- **异步IO** - AsyncIO 支持高并发评估
- **向量检索** - 关键词匹配 RAG（可升级为向量检索）

---

## 📁 项目结构

```
CreditScoringSystem/
│
├── app.py                     📊 Streamlit 前端
├── test_all.py                🧪 测试脚本
├── README.md                  📄 文档
├── pyproject.toml             📦 项目配置
│
├── data/                      📂 数据目录
│   ├── GiveMeSomeCredit/      📊 数据集 + 模型文件
│   │   ├── cs-training.csv    📈 训练数据
│   │   ├── credit_model.json  🤖 XGBoost 模型
│   │   └── xgboost_trainer.py 🔧 模型训练脚本
│   ├── knowledge_base/        📚 RAG 知识库
│   │   ├── regulations.md     📜 信贷法规
│   │   └── risk_cases.md     ⚠️ 风险案例
│   └── test_samples.json     🧪 测试样本
│
└── mini_agent/                🐍 Python 后端
    ├── web/api.py             🌐 FastAPI
    ├── multi_agent/           🤖 多智能体系统
    │   ├── graph.py           📈 LangGraph
    │   └── agents/            👥 三 Agent
    ├── tools/                 🔧 工具集
    │   └── credit_tools.py   💰 信贷工具
    ├── llm/                  🧠 LLM 客户端
    ├── database.py            💾 SQLite (评估历史)
    └── config/               ⚙️ 配置
        ├── config.yaml        🔑 API 密钥配置
        └── config-example.yaml
```

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 2️⃣ 配置

```bash
cp mini_agent/config/config-example.yaml mini_agent/config/config.yaml
```

编辑 `config.yaml`：
```yaml
llm:
  provider: "openai"
  api_key: "YOUR_API_KEY"
  model: "gpt-4"
```

### 3️⃣ 启动

```bash
# 终端 1: 后端
python -m uvicorn mini_agent.web.api:app --reload --port 8000

# 终端 2: 前端
streamlit run app.py
```

**访问**：
- 前端 → http://localhost:8501
- API docs → http://localhost:8000/docs

### 4️⃣ 测试

```bash
python test_all.py
```

---

## 📡 API 接口

### 单笔评估

```bash
POST /api/credit/evaluate
```

**请求：**
```json
{
  "numeric_data": {
    "age": 35,
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
    "application_statement": "贷款用于房屋装修",
    "credit_remarks": "信用良好"
  }
}
```

**响应：**
```json
{
  "final_decision": "approve",
  "decision_reason": "综合评估通过",
  "numeric_result": {
    "credit_score": 82,
    "probability_default": 0.15,
    "risk_level": "low"
  },
  "credit_report": {
    "report_id": "A1B2C3D4",
    "final_decision": "approve",
    "overall_score": 82
  }
}
```

### 批量评估

```bash
POST /api/credit/batch-evaluate
```

**请求：**
```json
{
  "applications": [
    {"numeric_data": {...}, "text_data": {...}},
    {"numeric_data": {...}, "text_data": {...}}
  ]
}
```

### 历史查询

```bash
GET /api/evaluations              # 评估历史列表
GET /api/evaluations/{id}        # 单条详情
GET /api/evaluations/statistics  # 统计信息
```

---

## 📊 性能指标

| 模型 | AUC | 提升 |
|------|-----|------|
| XGBoost | **0.85** | — |
| LR (对比) | 0.68 | +24.8% |

---

## ⚙️ 配置

### config.yaml 示例

```yaml
llm:
  provider: "openai"      # openai / minimax / anthropic
  api_key: "sk-xxx"
  model: "gpt-4"
  retry:
    enabled: true
    max_retries: 3
```

### 风控规则

编辑 `mini_agent/tools/credit_tools.py` 中的规则

---

## 🧪 常见问题

### Q: 前端连接不上后端？
```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 重新启动后端
python -m uvicorn mini_agent.web.api:app --reload --port 8000
```

### Q: API 返回 500 错误？
检查 `mini_agent/config/config.yaml` 中的 LLM API Key 是否正确

### Q: 如何查看评估历史？
访问 http://localhost:8501 或调用 `GET /api/evaluations`

### Q: 评估历史数据存在哪里？
SQLite 数据库位于 `mini_agent/data/evaluation_history.db`

---

<div align="center">

**MIT License** · Created for Credit Risk Management Demo

</div>
