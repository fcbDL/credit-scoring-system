# 💰 基于多智能体协同的大语言模型信贷评分系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-AUC%200.85-yellow.svg)

**基于 LangGraph + LLM 的多智能体协同风控决策系统**

</div>

---

## ✨ 功能特性

### 🎯 核心能力

| 功能 | 说明 |
|---|---|
| 🤖 **多智能体协同** | 数值分析 + 语义审计 + 主控决策 三 Agent 协作 |
| 📊 **XGBoost 评分** | 基于 GiveMeSomeCredit 数据集训练，AUC 达 0.85 |
| 🔍 **语义风险分析** | 基于 LLM 进行文本分析，识别隐性风险 |
| ⚖️ **规则引擎** | 5 条硬性风控规则自动匹配 |
| ⚡ **冲突检测** | 数值与语义结果冲突时自动触发二次审计 |
| 📋 **完整报告** | 自动生成结构化风控报告，含决策理由 |
| 📚 **RAG 知识库** | 信贷法规 + 风险案例检索，增强语义分析 |

### 📈 性能指标

```
┌─────────────────────────────────────────┐
│  XGBoost AUC:  0.85  ████████████  ✅ │
│  LR AUC:       0.68  ███████            │
│  提升:        +24.8%                     │
└─────────────────────────────────────────┘
```

---

## 🛠️ 技术栈

### 核心框架

| 类别 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 🤖 Agent 框架 | LangGraph | ≥ 0.2 | 基于状态机的多智能体编排框架 |
| 🧠 大语言模型 | OpenAI/MiniMax/Claude | - | 支持多提供商切换 |
| 📈 数值模型 | XGBoost | ≥ 2.0 | 信贷评分核心模型 |
| 🌐 后端框架 | FastAPI | ≥ 0.100 | 高性能 REST API |
| 🎨 前端框架 | Streamlit | - | 数据仪表盘，快速原型 |
| 📊 可视化 | Plotly | - | 评分仪表盘、雷达图、柱状图 |

### 数据处理与工具

| 类别 | 技术 | 说明 |
|------|------|------|
| 📊 数据集 | GiveMeSomeCredit | 美国信贷数据集，12万+样本 |
| 🔧 配置管理 | PyYAML | YAML 格式配置文件 |
| 📝 日志 | logging | 自定义日志系统 |
| 🔄 重试机制 | tenacity | API 调用失败自动重试 |
| 📚 RAG | 关键词检索 | 本地知识库检索 |

---

## 🏗️ 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                           客户端层                                  │
│    ┌─────────────────┐                    ┌─────────────────┐       │
│    │  Streamlit 前端  │                    │    CLI 终端     │       │
│    │   localhost:5173│                    │   快速验证      │       │
│    └────────┬────────┘                    └────────┬────────┘       │
└─────────────┼──────────────────────────────────────┼──────────────────┘
              │                                      │
              ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           API 网关层                                 │
│    ┌─────────────────────────────────────────────────────────┐       │
│    │                    FastAPI 后端                         │       │
│    │              POST /api/credit/evaluate                  │       │
│    │              GET  /health                              │       │
│    └─────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        LangGraph 状态机层                            │
│                                                                     │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    │
│   │  START   │───▶│ numeric  │───▶│semantic  │───▶│supervisor│    │
│   │   开始   │    │  Agent   │    │  Agent   │    │  Agent   │    │
│   └──────────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘    │
│                        │                │               │           │
│                        └────────────────┼───────────────┘           │
│                                     冲突检测                         │
└─────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           工具层                                     │
│   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│   │  XGBoostScore │  │ RiskRuleEngine │  │  RAGRetrieval  │        │
│   │    数值评分    │  │    规则匹配    │  │    知识库检索  │        │
│   └────────────────┘  └────────────────┘  └────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

### 智能体分工

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| **NumericAgent** | 数值分析 | 结构化信贷数据 | 风险分数、异常指标、规则匹配 |
| **SemanticAgent** | 语义审计 | 文本材料 + RAG 检索 | 语义风险等级、风险点 |
| **SupervisorAgent** | 决策整合 | Agent 分析结果 | 最终决策 + 理由 |

---

## 📁 项目结构

```bash
CreditScoringSystem/
│
├── app.py                         # 📊 Streamlit 前端仪表盘
│
├── mini_agent/                    # 🐍 Python 后端
│   │
│   ├── cli.py                    # 🖥️ CLI 命令行入口
│   ├── config.py                  # ⚙️ 全局配置加载
│   ├── logger.py                 # 📝 日志配置
│   ├── retry.py                  # 🔄 重试策略
│   │
│   ├── llm/                      # 🤖 LLM 客户端
│   │   ├── base.py               # 抽象基类
│   │   ├── llm_wrapper.py        # 统一封装
│   │   ├── anthropic_client.py  # Claude 适配
│   │   └── openai_client.py      # OpenAI 适配
│   │
│   ├── tools/                    # 🔧 工具集
│   │   ├── credit_tools.py       # 💰 信贷工具
│   │   │   ├── XGBoostScoreTool     # 数值评分
│   │   │   ├── RiskRuleEngineTool   # 规则引擎
│   │   │   └── RAGRetrievalTool     # RAG 检索
│   │   └── ...
│   │
│   ├── multi_agent/              # 🔄 多智能体系统
│   │   ├── graph.py              # LangGraph 状态机
│   │   ├── state.py              # 状态类型定义
│   │   └── agents/
│   │       ├── numeric.py        # 📊 数值分析 Agent
│   │       ├── semantic.py       # 🔍 语义审计 Agent
│   │       └── supervisor.py     # 🎯 主控决策 Agent
│   │
│   └── web/                      # 🌐 Web 服务
│       └── api.py                # FastAPI 后端
│
├── data/                         # 📂 数据目录
│   ├── GiveMeSomeCredit/        # 训练数据
│   │   ├── cs-training.csv       # 训练集
│   │   └── credit_model.json    # XGBoost 模型
│   ├── knowledge_base/          # 📚 RAG 知识库
│   │   ├── regulations.md       # 信贷法规
│   │   └── risk_cases.md        # 风险案例
│   └── test_samples.json        # 测试样本
│
├── mini_agent/config/
│   └── config.yaml               # 配置文件
│
├── requirements.txt              # 📦 Python 依赖
├── pyproject.toml                # 📦 项目配置
└── README.md                     # 📄 文档
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- API Key (MiniMax / OpenAI / Anthropic)

### 1️⃣ 安装依赖

```bash
# 后端
pip install -r requirements.txt

# 前端
cd frontend && npm install
```

### 2️⃣ 配置

```bash
cp mini_agent/config/config-example.yaml mini_agent/config/config.yaml
```

编辑 `mini_agent/config/config.yaml`：

```yaml
llm:
  provider: "openai"           # 支持: openai / minimax / anthropic
  api_key: "YOUR_API_KEY"      # 填入你的 API Key
  model: "gpt-4"               # 模型名称

server:
  host: "0.0.0.0"
  port: 8000
```

### 3️⃣ 启动服务

**后端 + 前端（同时运行）：**

```bash
# 终端 1: 启动后端 API
python -m uvicorn mini_agent.web.api:app --reload --port 8000

# 终端 2: 启动 Streamlit 前端
streamlit run app.py
```

访问：
- 前端界面 👉 http://localhost:8501
- API 文档 👉 http://localhost:8000/docs

### 4️⃣ CLI 模式

```bash
python -m mini_agent.cli --mode multi --task '{
  "numeric_data": {
    "age": 35,
    "income": 80000,
    "credit_history_length": 5,
    "debt_to_income_ratio": 0.3,
    "employment_length": 3,
    "loan_amount": 50000,
    "loan_purpose": "personal",
    "existing_loans": 1,
    "payment_history": 0.9
  },
  "text_data": {
    "application_statement": "贷款用于房屋装修",
    "credit_remarks": "信用良好"
  }
}'
```

---

## 📝 API 参考

### 评估接口

```
POST /api/credit/evaluate
```

**请求体：**

```json
{
  "numeric_data": {
    "age": 35,
    "income": 80000,
    "credit_history_length": 5,
    "debt_to_income_ratio": 0.3,
    "employment_length": 3,
    "loan_amount": 50000,
    "loan_purpose": "personal",
    "existing_loans": 1,
    "payment_history": 0.9
  },
  "text_data": {
    "application_statement": "贷款用于房屋装修",
    "credit_remarks": "信用良好"
  }
}
```

**响应示例：**

```json
{
  "final_decision": "approve",
  "decision_reason": "综合评估通过",
  "numeric_result": {
    "credit_score": 72.5,
    "probability_default": 0.12,
    "risk_level": "medium",
    "model_used": "xgboost"
  },
  "semantic_risk": {
    "repayment_willingness": "high",
    "industry_risk": "low",
    "fraud_indicators": []
  },
  "conflict_detected": false,
  "trace": [
    {"node": "supervisor", "action": "plan", "plan": "Invoke numeric and semantic agents"},
    {"agent": "numeric", "action": "xgboost_score", "result": "Credit score: 74.4"},
    {"agent": "semantic", "action": "rag_retrieval", "results_count": 3},
    {"agent": "semantic", "action": "llm_analysis", "result": "..."}
  ],
  "credit_report": {...}
}
```

### 健康检查

```
GET /health
```

### 评估历史接口

```
GET /api/evaluations?limit=50&offset=0
```

**响应示例：**
```json
{
  "evaluations": [
    {"id": 1, "final_decision": "approve", "credit_score": 74.4, "risk_level": "low", "created_at": "2026-04-05 10:00:00"}
  ],
  "total": 1
}
```

```
GET /api/evaluations/{eval_id}
```

```
GET /api/evaluations/statistics
```

**响应示例：**
```json
{
  "total": 10,
  "decisions": {"approve": 7, "reject": 3},
  "average_credit_score": 68.5,
  "risk_distribution": {"low": 5, "medium": 3, "high": 2}
}
```

---

## 📊 毕设进度汇报

### 已完成工作

| 模块 | 状态 | 说明 |
|------|------|------|
| 多 Agent 编排 | ✅ 完成 | LangGraph 状态机，三 Agent 协同 |
| XGBoost 评分 | ✅ 完成 | AUC 0.85，GiveMeSomeCredit 数据集 |
| 规则引擎 | ✅ 完成 | 5 条硬性风控规则 |
| 语义分析 | ✅ 完成 | LLM 文本风险识别 + RAG 知识增强 |
| 冲突检测 | ✅ 完成 | 数值 vs 语义，自动触发审计 |
| 报告生成 | ✅ 完成 | 结构化风控报告 |
| FastAPI 服务 | ✅ 完成 | REST API + CORS |
| Streamlit 前端 | ✅ 完成 | 数据仪表盘 + 批量评估 |
| CLI 工具 | ✅ 完成 | 命令行快速评估 |
| RAG 知识库 | ✅ 完成 | 关键词检索法规+案例 |
| 评估历史 | ✅ 完成 | SQLite 存储、统计 API |
| 批量评估 | ✅ 完成 | 表单+JSON 导入 |

### 技术亮点

1. **多智能体协同架构**：LangGraph 状态机应用于信贷风控领域
2. **数值+语义双通道分析**：机器学习与传统规则互补
3. **冲突检测机制**：自动识别模型与专家知识的分歧
4. **RAG 知识增强**：结合信贷法规和风险案例进行语义分析
5. **结构化报告生成**：一键输出合规风控报告

### 遇到的问题与解决方案

| 困难 | 解决方案 |
|------|----------|
| XGBoost 特征映射 | 设计用户友好接口，自动转换原始特征 |
| LLM 调用不稳定 | 实现指数退避重试机制 |
| 前端跨域请求 | 配置 FastAPI CORS 中间件 |
| Agent 状态管理 | 使用 LangGraph TypedDict 规范化状态 |
| RAG 匹配不准确 | 优化关键词提取和 relevance 算法 |

### 时间规划（⚠️ 4月15日前完成）

```
当前 ←─────── 4月8日 ────────→ 4月15日
     │                              │
已完成 ██████████████████████        截止线 ││
                              ││
[剩余任务 - 共约 1 周]         ││
                              ││
├── 4/8:     全面测试完成 ────┤│
├── 4/9-4/14: 论文撰写 ──────┤│
└── 4/15:     答辩准备 ───────┘│
```

| 阶段 | 时间 | 任务 |
|------|------|------|
| **RAG完成** | 3/24 - 4/3 | RAG 知识库、关键词检索 |
| **评估历史** | 4/3 - 4/5 | SQLite 存储、评估历史 API |
| **批量评估** | 4/5 - 4/7 | 表单+JSON 导入、友好展示 |
| **全面测试** | 4/8 - 4/8 | XGBoost/规则引擎/RAG/数据库/API |
| **论文撰写** | 4/9 - 4/14 | 论文定稿 |
| **答辩准备** | 4/15 | 演示准备 |

---

<div align="center">

**Star ⭐ 如果对你有帮助！**

</div>
