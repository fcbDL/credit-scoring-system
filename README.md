# 💰 基于多智能体协同的大语言模型信贷评分系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-AUC%200.85-yellow.svg)

**基于 LangGraph + MiniMax 的多智能体协同风控决策系统**

</div>

---

## ✨ 功能特性

### 🎯 核心能力

| 功能 | 说明 |
|---|---|
| 🤖 **多智能体协同** | 数值分析 + 语义审计 + 主控决策 三 Agent 协作 |
| 📊 **XGBoost 评分** | 基于 GiveMeSomeCredit 数据集训练，AUC 达 0.85 |
| 🔍 **语义风险分析** | 基于 MiniMax LLM 进行文本分析，识别隐性风险 |
| ⚖️ **规则引擎** | 硬性风控规则自动匹配，支持自定义规则 |
| ⚡ **冲突检测** | 数值与语义结果冲突时自动触发二次审计 |
| 📋 **完整报告** | 自动生成结构化风控报告，含决策理由 |

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
| 🧠 大语言模型 | MiniMax | M2.5 | 主推理模型，支持语义分析 |
| 🧠 LLM 备选 | OpenAI GPT-4 / Claude | - | 可切换的备选模型 |
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

### 依赖环境

**后端 (Python)**
```
langgraph>=0.2
langchain-core>=0.3
langchain-minimax>=0.1
xgboost>=2.0
fastapi>=0.100
uvicorn>=0.23
pydantic>=2.0
pyyaml>=6.0
streamlit>=1.40
plotly>=5.24
```

**前端 (Python)**
```
streamlit
plotly
requests
```

---

## 🏗️ 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                           客户端层                                  │
│    ┌─────────────────┐                    ┌─────────────────┐       │
│    │  Streamlit UI   │                    │    CLI 终端     │       │
│    │  仪表盘 + 报告  │                    │   快速验证      │       │
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
│   │  XGBoostScore │  │ RiskRuleEngine │  │  LLM Client    │        │
│   │    数值评分    │  │    规则匹配    │  │   语义分析     │        │
│   └────────────────┘  └────────────────┘  └────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

### 智能体分工

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| **NumericAgent** | 数值分析 | 结构化信贷数据 | 风险分数、异常指标 |
| **SemanticAgent** | 语义审计 | 文本材料、备注 | 语义风险等级、风险点 |
| **SupervisorAgent** | 决策整合 | Agent 分析结果 | 最终决策 + 理由 |

---

## 📁 项目结构

```bash
CreditScoringSystem/
│
├── app.py                        # 📊 Streamlit 前端仪表盘
│
├── mini_agent/                   # 🐍 Python 后端
│   │
│   ├── cli.py                   # 🖥️ CLI 命令行入口
│   ├── config.py                # ⚙️ 全局配置加载
│   ├── logger.py                # 📝 日志配置
│   ├── retry.py                 # 🔄 重试策略
│   │
│   ├── llm/                     # 🤖 LLM 客户端
│   │   ├── base.py              # 抽象基类
│   │   ├── llm_wrapper.py       # 统一封装
│   │   ├── anthropic_client.py  # Claude 适配
│   │   └── openai_client.py      # GPT 适配
│   │
│   ├── tools/                   # 🔧 工具集
│   │   ├── credit_tools.py      # 💰 信贷工具
│   │   │   ├── XGBoostScoreTool     # 数值评分
│   │   │   ├── RiskRuleEngineTool   # 规则引擎
│   │   │   └── RAGRetrievalTool     # RAG 检索
│   │   ├── bash_tool.py         # 终端命令执行
│   │   ├── file_tools.py        # 文件操作
│   │   ├── note_tool.py         # 笔记工具
│   │   └── skill_tool.py        # 技能加载
│   │
│   ├── multi_agent/             # 🔄 多智能体系统
│   │   ├── graph.py             # LangGraph 状态机定义
│   │   ├── state.py             # 状态类型定义
│   │   └── agents/
│   │       ├── numeric.py       # 📊 数值分析 Agent
│   │       ├── semantic.py      # 🔍 语义审计 Agent
│   │       └── supervisor.py    # 🎯 主控决策 Agent
│   │
│   └── web/                     # 🌐 Web 服务
│       └── api.py               # FastAPI 后端
│
├── data/                        # 📂 数据目录
│   ├── GiveMeSomeCredit/       # 训练数据
│   │   ├── cs-training.csv      # 训练集 (12万+样本)
│   │   └── credit_model.json    # XGBoost 模型文件
│   └── test_samples.json        # 测试样本
│
├── requirements.txt             # 📦 Python 依赖
├── pyproject.toml               # 📦 项目配置
└── README.md                    # 📄 文档
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- API Key (MiniMax / OpenAI / Anthropic)

### 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
# 或
pip install streamlit plotly requests
```

### 2️⃣ 配置

```bash
cp mini_agent/config/config-example.yaml mini_agent/config/config.yaml
```

编辑 `mini_agent/config/config.yaml`：

```yaml
llm:
  provider: "minimax"           # 支持: minimax / openai / anthropic
  api_key: "YOUR_API_KEY"       # 填入你的 API Key
  model: "MiniMax-M2.5"          # 模型名称

server:
  host: "0.0.0.0"
  port: 8000
```

### 4️⃣ 启动服务

**后端 + 前端（同时运行）：**

```bash
# 终端 1: 启动后端 API
python -m uvicorn mini_agent.web.api:app --reload --port 8000

# 终端 2: 启动前端
cd frontend && npm run dev
```

访问：
- 前端界面 👉 http://localhost:5173
- API 文档 👉 http://localhost:8000/docs

### 5️⃣ CLI 模式

```bash
python -m mini_agent.cli --mode multi --task '{
  "numeric_data": {
    "age": 35,
    "income": 80000,
    "credit_history_length": 5,
    "debt_to_income_ratio": 0.3,
    "employment_length": 3,
    "loan_amount": 50000,
    "loan_purpose": "home",
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
    "loan_purpose": "home",
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
    "features_importance": {...}
  },
  "semantic_risk": {
    "repayment_willingness": "high",
    "industry_risk": "low",
    "fraud_indicators": [],
    "concerns": []
  },
  "conflict_detected": false,
  "trace": [...],
  "credit_report": {
    "report_id": "497F28B2",
    "evaluation_time": "2026-03-23 12:00:00",
    "overall_score": 72,
    "final_decision": "approve",
    ...
  }
}
```

### 健康检查

```
GET /health
```

---

## 🔧 自定义配置

### 添加风控规则

编辑 `mini_agent/tools/credit_tools.py` 中的 `RiskRuleEngineTool`：

```python
CUSTOM_RULES = [
    {"name": "收入负债比", "condition": "debt_to_income_ratio <= 0.5"},
    {"name": "年龄限制", "condition": "18 <= age <= 65"},
    {"name": "贷款金额上限", "condition": "loan_amount <= income * 5"},
]
```

### 切换 LLM 模型

修改 `config.yaml` 中的 `llm.provider`：

| Provider | Model |
|----------|-------|
| `minimax` | MiniMax-M2.5 |
| `openai` | gpt-4, gpt-4-turbo |
| `anthropic` | claude-3-opus, claude-3-sonnet |

---

## 📊 毕设进度汇报

### 已完成工作

| 模块 | 状态 | 说明 |
|------|------|------|
| 多 Agent 编排 | ✅ 完成 | LangGraph 状态机，三 Agent 协同 |
| XGBoost 评分 | ✅ 完成 | AUC 0.85，GiveMeSomeCredit 数据集 |
| 规则引擎 | ✅ 完成 | 4 条硬性风控规则 |
| 语义分析 | ✅ 完成 | MiniMax LLM 文本风险识别 |
| 冲突检测 | ✅ 完成 | 数值 vs 语义，自动触发审计 |
| 报告生成 | ✅ 完成 | 结构化风控报告 |
| FastAPI 服务 | ✅ 完成 | REST API + CORS |
| Streamlit 前端 | ✅ 完成 | 数据仪表盘 + 报告可视化 |
| CLI 工具 | ✅ 完成 | 命令行快速评估 |

### 技术亮点

1. **多智能体协同架构**：LangGraph 状态机应用于信贷风控领域
2. **数值+语义双通道分析**：机器学习与传统规则互补
3. **冲突检测机制**：自动识别模型与专家知识的分歧
4. **结构化报告生成**：一键输出合规风控报告

### 遇到的问题与解决方案

| 困难 | 解决方案 |
|------|----------|
| XGBoost 特征映射 | 设计用户友好接口，自动转换原始特征 |
| LLM 调用不稳定 | 实现指数退避重试机制 |
| 前端跨域请求 | 配置 FastAPI CORS 中间件 |
| Agent 状态管理 | 使用 LangGraph TypedDict 规范化状态 |

### 后续开发计划

#### 📦 功能完善

| 功能 | 说明 |
|------|------|
| RAG 知识库 | 接入真实信贷法规知识库 |
| 评估历史接口 | 数据库存储评估记录 |
| 批量评估 API | 支持批量导入数据评估 |
| 性能优化 | 异步处理、缓存机制 |

#### 🔧 模型优化

| 功能 | 说明 |
|------|------|
| 模型更新 | 使用最新数据重新训练 |
| A/B 测试 | 对比不同模型效果 |
| 阈值调优 | 优化决策阈值 |

### 时间规划（⚠️ 4月15日前完成）

```
当前 ←─────── 4月1日 ────────→ 4月15日
     │                              │
已完成 ████████░░░░░░          截止线 ││
                              ││
[剩余任务 - 共约 2 周]         ││
                              ││
├── 4/1-4/7:  RAG 知识库完善 ──┤│
├── 4/8-4/14: 测试与部署 ─────┤│
└── 4/15:     论文/演示准备 ──┘│
```

| 阶段 | 时间 | 任务 |
|------|------|------|
| **前端完成** | 3/24 - 4/1 | Streamlit 仪表盘、评分仪表盘、图表可视化 |
| **功能完善** | 4/1 - 4/7 | RAG 知识库、批量评估接口 |
| **收尾测试** | 4/8 - 4/14 | 全面测试、部署文档 |
| **答辩准备** | 4/15 | 论文定稿、演示准备 |

---

<div align="center">

**Star ⭐ 如果对你有帮助！**

</div>
