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
│  XGBoost AUC:  0.85  ████████████  ✅  │
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
| 🎨 前端框架 | Streamlit | ≥ 1.28 | 交互式 Web 界面 |

### 数据处理与工具

| 类别 | 技术 | 说明 |
|------|------|------|
| 📊 数据集 | GiveMeSomeCredit | 美国信贷数据集，12万+样本 |
| 🔧 配置管理 | PyYAML | YAML 格式配置文件 |
| 📝 日志 | logging | 自定义日志系统 |
| 🔄 重试机制 | tenacity | API 调用失败自动重试 |

### 依赖环境

```
langgraph>=0.2
langchain-core>=0.3
langchain-minimax>=0.1
xgboost>=2.0
fastapi>=0.100
uvicorn>=0.23
streamlit>=1.28
pydantic>=2.0
pyyaml>=6.0
```

---

## 🏗️ 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                           客户端层                                  │
│    ┌─────────────────┐                    ┌─────────────────┐       │
│    │   Streamlit UI  │                    │    CLI 终端     │       │
│    │  可视化 + 报告   │                    │   快速验证      │       │
│    └────────┬────────┘                    └────────┬────────┘       │
└─────────────┼──────────────────────────────────────┼──────────────────┘
              │                                      │
              ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           API 网关层                                 │
│    ┌─────────────────────────────────────────────────────────┐       │
│    │                    FastAPI 后端                         │       │
│    │              POST /api/credit/evaluate                  │       │
│    │              GET  /api/credit/health                    │       │
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
│   │  XGBoostScore  │  │ RiskRuleEngine │  │  LLM Client    │        │
│   │    数值评分     │  │    规则匹配     │  │  语义分析      │        │
│   └────────────────┘  └────────────────┘  └────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

### 智能体分工

| Agent | 职责 | 输入 | 输出 |
|-------|------|------|------|
| **NumericAgent** | 数值分析 | 结构化信贷数据 | 风险分数、异常指标 |
| **SemanticAgent** | 语义审计 | 文本材料、备注 | 语义风险等级、风险点 |
| **SupervisorAgent** | 决策整合 | Agent 分析结果 | 最终决策 + 理由 |

### 数据流

```
用户输入 ──▶ 数值数据 ──▶ XGBoost ──▶ 风险分数 ──┐
                                                  ├─▶ 冲突检测 ──▶ Supervisor ──▶ 决策
        ──▶ 文本数据 ──▶ LLM ──▶ 语义风险 ──────┘
```

---

## 📁 项目结构

```bash
CreditScoringSystem/
│
├── mini_agent/                    # 核心代码包
│   │
│   ├── cli.py                     # 🖥️ CLI 命令行入口
│   ├── config.py                  # ⚙️ 全局配置加载
│   ├── logger.py                  # 📝 日志配置
│   ├── retry.py                   # 🔄 重试策略
│   │
│   ├── llm/                       # 🤖 LLM 客户端
│   │   ├── base.py               # 抽象基类
│   │   ├── llm_wrapper.py        # 统一封装
│   │   ├── anthropic_client.py  # Claude 适配
│   │   └── openai_client.py      # GPT 适配
│   │
│   ├── tools/                     # 🔧 工具集
│   │   ├── credit_tools.py       # 💰 信贷工具
│   │   │   ├── XGBoostScoreTool      # 数值评分
│   │   │   ├── RiskRuleEngineTool    # 规则引擎
│   │   │   └── RAGRetrievalTool     # RAG 检索
│   │   ├── bash_tool.py          # 终端命令执行
│   │   ├── file_tools.py         # 文件操作
│   │   ├── note_tool.py          # 笔记工具
│   │   └── skill_tool.py         # 技能加载
│   │
│   ├── multi_agent/               # 🔄 多智能体系统
│   │   ├── graph.py              # LangGraph 状态机定义
│   │   ├── state.py              # 状态类型定义
│   │   └── agents/
│   │       ├── numeric.py        # 📊 数值分析 Agent
│   │       ├── semantic.py       # 🔍 语义审计 Agent
│   │       └── supervisor.py     # 🎯 主控决策 Agent
│   │
│   ├── web/                       # 🌐 Web 服务
│   │   ├── api.py                # FastAPI 后端
│   │   └── app.py                # Streamlit 前端
│   │
│   └── utils/                     # 🛠️ 工具函数
│       └── terminal_utils.py     # 终端美化
│
├── data/                          # 📂 数据目录
│   ├── GiveMeSomeCredit/         # 训练数据
│   │   ├── cs-training.csv       # 训练集 (12万+样本)
│   │   └── credit_model.json      # XGBoost 模型文件
│   └── test_samples.json          # 测试样本
│
├── requirements.txt              # 📦 依赖清单
├── pyproject.toml                 # 📦 项目配置
└── README.md                      # 📄 文档
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- API Key (MiniMax / OpenAI / Anthropic)

### 1️⃣ 安装依赖

```bash
# 克隆项目
git clone https://github.com/your-repo/CreditScoringSystem.git
cd CreditScoringSystem

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 配置

```bash
# 复制配置模板
cp mini_agent/config/config-example.yaml mini_agent/config/config.yaml
```

编辑 `mini_agent/config/config.yaml`：

```yaml
# LLM 配置
llm:
  provider: "minimax"           # 支持: minimax / openai / anthropic
  api_key: "YOUR_API_KEY"       # 填入你的 API Key
  model: "MiniMax-M2.5"         # 模型名称

# 服务器配置
server:
  host: "0.0.0.0"
  port: 8000
```

### 3️⃣ 启动服务

**方式一：Web 界面（推荐）**

```bash
# 启动 FastAPI 后端
python -m uvicorn mini_agent.web.api:app --reload --port 8000

# 启动 Streamlit 前端（新终端）
python -m streamlit run mini_agent/web/app.py
```

访问 👉 http://localhost:8501

**方式二：CLI 模式**

```bash
# 单次评估
python -m mini_agent.cli --mode single --task '{
  "numeric_data": {
    "age": 35,
    "income": 120000,
    "loan_amount": 80000,
    "payment_history": 0.95,
    "debt_to_income_ratio": 0.25
  },
  "text_data": {
    "application_statement": "贷款用于房屋装修",
    "credit_remarks": "信用记录良好，无逾期"
  }
}'
```

**方式三：Python API**

```python
import asyncio
from mini_agent.multi_agent import create_credit_graph
from mini_agent.multi_agent.agents import NumericAgent, SemanticAgent, SupervisorAgent
from mini_agent.tools.credit_tools import XGBoostScoreTool, RiskRuleEngineTool
from mini_agent.llm import LLMClient

async def evaluate_credit():
    # 初始化 LLM
    llm = LLMClient(
        api_key="your-api-key",
        provider="minimax",
        model="MiniMax-M2.5"
    )

    # 初始化工具
    tools = [XGBoostScoreTool(), RiskRuleEngineTool()]

    # 创建 Agent
    numeric_agent = NumericAgent(llm, tools)
    semantic_agent = SemanticAgent(llm, tools)
    supervisor_agent = SupervisorAgent(llm, tools)

    # 构建状态机
    graph = create_credit_graph(
        numeric_agent,
        semantic_agent,
        supervisor_agent
    )

    # 输入数据
    user_input = {
        "numeric_data": {
            "age": 35,
            "income": 120000,
            "loan_amount": 80000,
            "payment_history": 0.95,
            "debt_to_income_ratio": 0.25
        },
        "text_data": {
            "application_statement": "贷款用于房屋装修",
            "credit_remarks": "信用记录良好"
        }
    }

    # 执行评估
    result = await graph.ainvoke({"user_input": user_input})

    # 输出结果
    print(f"决策: {result['final_decision']}")
    print(f"理由: {result['reasoning']}")

asyncio.run(evaluate_credit())
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
    "income": 120000,
    "loan_amount": 80000,
    "payment_history": 0.95,
    "debt_to_income_ratio": 0.25
  },
  "text_data": {
    "application_statement": "贷款用于房屋装修",
    "credit_remarks": "信用记录良好"
  }
}
```

**响应示例：**

```json
{
  "decision": "approved",
  "risk_level": "low",
  "xgboost_score": 0.82,
  "semantic_risk": "low",
  "rule_violations": [],
  "report": "经综合评估，该申请人信用风险较低，建议批准贷款申请...",
  "agent_trace": {
    "numeric_agent": { "status": "completed", "score": 0.82 },
    "semantic_agent": { "status": "completed", "risk": "low" },
    "supervisor_agent": { "status": "completed", "decision": "approved" }
  }
}
```

### 健康检查

```
GET /api/credit/health
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

<div align="center">

**Star ⭐ 如果对你有帮助！**

</div>
