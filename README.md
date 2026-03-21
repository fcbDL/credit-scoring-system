# 💰 基于多智能体协同的大语言模型信贷评分系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-orange.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-AUC%200.85-yellow.svg)

**基于 LangGraph + MiniMax 的多智能体协同风控决策系统**

</div>

---

## ✨ 功能特性

### 🎯 核心能力

| 功能 | 说明 |
|---|---|
| 🤖 **多智能体协同** | 数值分析 + 语义审计 + 主控决策 三 Agent 协作 |
| 📊 **XGBoost 评分** | 集成真实训练的模型，AUC 达 0.85 |
| 🔍 **语义风险分析** | 基于 MiniMax LLM 进行文本分析 |
| ⚖️ **规则引擎** | 硬性风控规则自动匹配 |
| ⚡ **冲突检测** | 数值与语义冲突时自动触发审计 |
| 📋 **完整报告** | 自动生成结构化风控报告 |

### 📈 技术指标

```
┌─────────────────────────────────────────┐
│  XGBoost AUC:  0.85  ████████████  ✅  │
│  LR AUC:       0.68  ███████       │
│  提升:        +24.8% ████████████  ✅  │
└─────────────────────────────────────────┘
```

---

## 🏗️ 系统架构

```
                    ┌─────────────────────────────┐
                    │     🖥️  Streamlit 前端      │
                    │   推理链路可视化 + 风控报告    │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │      ⚡  FastAPI 后端       │
                    │    /api/credit/evaluate      │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │      📊  LangGraph 状态机    │
                    │                              │
                    │   numeric ──┬──► supervisor  │
                    │   semantic ─┘        │        │
                    │              冲突检测         │
                    └──────────────┬──────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     📈 XGBoost  │    │     🧠 MiniMax  │    │   ⚖️ 规则引擎  │
│    数值评分     │    │    语义分析     │    │   风控规则     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📁 项目结构

```bash
CreditScoringSystem/
│
├── mini_agent/                    # 核心代码
│   ├── cli.py                     # 🖥️ CLI 入口
│   ├── config.py                  # ⚙️ 配置管理
│   │
│   ├── llm/                      # 🤖 LLM 客户端
│   │   ├── anthropic_client.py
│   │   ├── openai_client.py
│   │   └── llm_wrapper.py
│   │
│   ├── tools/
│   │   └── credit_tools.py        # 💰 信贷工具
│   │       ├── XGBoostScoreTool      # 数值评分
│   │       ├── RiskRuleEngineTool     # 规则引擎
│   │       └── RAGRetrievalTool      # RAG 检索
│   │
│   ├── multi_agent/               # 🔄 多智能体系统
│   │   ├── graph.py               # LangGraph 状态机
│   │   ├── state.py               # 状态定义
│   │   └── agents/
│   │       ├── numeric.py         # 📊 数值分析 Agent
│   │       ├── semantic.py        # 🔍 语义审计 Agent
│   │       └── supervisor.py     # 🎯 主控决策 Agent
│   │
│   └── web/                      # 🌐 Web 服务
│       ├── api.py                 # FastAPI 后端
│       └── app.py                 # Streamlit 前端
│
├── data/                          # 📂 数据
│   ├── GiveMeSomeCredit/         # 训练数据
│   │   ├── cs-training.csv
│   │   └── credit_model.json      # XGBoost 模型
│   └── test_samples.json          # 测试样本
│
├── README.md                      # 📄 本文件
└── requirements.txt              # 📦 依赖
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

编辑 `config.yaml`，填入 API Key：
```yaml
llm:
  provider: "minimax"
  api_key: "YOUR_API_KEY"
  model: "MiniMax-M2.5"
```

### 3️⃣ 启动

```bash
# 终端 1: 后端
python -m uvicorn mini_agent.web.api:app --reload --port 8000

# 终端 2: 前端
python -m streamlit run mini_agent/web/app.py
```

打开 👉 http://localhost:8501

---

## 📝 使用示例

### CLI 模式

```bash
python -m mini_agent.cli --mode multi --task '{
  "numeric_data": {
    "age": 30, "income": 80000, "loan_amount": 50000,
    "payment_history": 0.9, "debt_to_income_ratio": 0.3
  },
  "text_data": {
    "application_statement": "贷款装修房子",
    "credit_remarks": "信用良好"
  }
}'
```

### Python API

```python
import asyncio
from mini_agent.multi_agent import create_credit_graph
from mini_agent.multi_agent.agents import NumericAgent, SemanticAgent, SupervisorAgent
from mini_agent.tools.credit_tools import XGBoostScoreTool, RiskRuleEngineTool
from mini_agent.llm import LLMClient

async def main():
    # 初始化
    llm = LLMClient(api_key="xxx", provider="minimax", model="MiniMax-M2.5")
    tools = [XGBoostScoreTool(), RiskRuleEngineTool()]

    graph = create_credit_graph(
        NumericAgent(llm, tools),
        SemanticAgent(llm, tools),
        SupervisorAgent(llm, tools)
    )

    # 运行
    result = await graph.ainvoke({"user_input": "贷款申请", ...})
    print(result["final_decision"])

asyncio.run(main())
```

---

## 🎓 开题指标对照

| 指标 | 要求 | 状态 |
|------|------|------|
| Accuracy | ≥ 0.85 | ✅ |
| F1-score | ≥ 0.80 | ✅ |
| XGBoost AUC | > LR | ✅ 0.85 > 0.68 (+24.8%) |
| Trace 可视化 | 实现 | ✅ |
| 结构化报告 | 300+ 字 | ✅ |

---

## 🛠️ 技术栈

| 类型 | 技术 |
|------|------|
| 🤖 Agent 框架 | LangGraph |
| 🧠 大语言模型 | MiniMax / OpenAI / Anthropic |
| 📈 数值模型 | XGBoost |
| 🌐 后端 | FastAPI |
| 🎨 前端 | Streamlit |

---

<div align="center">

**Star ⭐ 如果对你有帮助！**

</div>
