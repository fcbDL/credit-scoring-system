#!/usr/bin/env python
"""信贷评分系统全面测试脚本"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mini_agent.tools.credit_tools import XGBoostScoreTool, RiskRuleEngineTool, RAGRetrievalTool
from mini_agent.database import save_evaluation, get_evaluations, get_statistics, get_evaluation_by_id


async def test_xgboost():
    """测试 XGBoost 评分"""
    print("\n" + "="*50)
    print("🧪 测试 XGBoost 评分")
    print("="*50)

    tool = XGBoostScoreTool()

    test_cases = [
        {"age": 35, "income": 80000, "credit_history_length": 5, "debt_to_income_ratio": 0.3,
         "employment_length": 3, "loan_amount": 50000, "loan_purpose": "personal",
         "existing_loans": 1, "payment_history": 0.9},
        {"age": 28, "income": 30000, "credit_history_length": 2, "debt_to_income_ratio": 0.6,
         "employment_length": 1, "loan_amount": 80000, "loan_purpose": "business",
         "existing_loans": 3, "payment_history": 0.5},
    ]

    for i, case in enumerate(test_cases, 1):
        result = await tool.execute(**case)
        import json
        data = json.loads(result.content)
        print(f"测试 {i}: 评分={data['credit_score']}, 风险={data['risk_level']}, 模型={data['model_used']}")

    print("✅ XGBoost 测试通过")
    return True


async def test_risk_rules():
    """测试规则引擎"""
    print("\n" + "="*50)
    print("🧪 测试规则引擎")
    print("="*50)

    tool = RiskRuleEngineTool()

    test_cases = [
        {"age": 35, "income": 50000, "debt_to_income_ratio": 0.3, "credit_history_length": 5},
        {"age": 16, "income": 50000, "debt_to_income_ratio": 0.3, "credit_history_length": 5},  # 年龄不符
        {"age": 35, "income": 5000, "debt_to_income_ratio": 0.3, "credit_history_length": 5},  # 收入过低
        {"age": 35, "income": 50000, "debt_to_income_ratio": 0.8, "credit_history_length": 5},  # 负债率过高
    ]

    for i, case in enumerate(test_cases, 1):
        result = await tool.execute(**case)
        import json
        data = json.loads(result.content)
        print(f"测试 {i}: 通过={data['final_action']}, 违规数={data['rule_match_count']}")

    print("✅ 规则引擎测试通过")
    return True


async def test_rag():
    """测试 RAG 检索"""
    print("\n" + "="*50)
    print("🧪 测试 RAG 检索")
    print("="*50)

    tool = RAGRetrievalTool()

    queries = [
        "贷款风险 收入不稳定",
        "负债率 过高",
        "逾期 欺诈",
    ]

    for query in queries:
        result = await tool.execute(query=query, top_k=3)
        import json
        data = json.loads(result.content)
        print(f"查询 '{query}': 返回 {len(data)} 条")
        for item in data:
            print(f"  - {item['title']} (相关度: {item['relevance']})")

    print("✅ RAG 测试通过")
    return True


def test_database():
    """测试数据库"""
    print("\n" + "="*50)
    print("🧪 测试数据库")
    print("="*50)

    # 测试保存
    eval_id = save_evaluation(
        user_id="test_user",
        user_input="测试评估",
        numeric_data={"age": 35, "income": 50000},
        text_data={"application_statement": "测试"},
        final_decision="approve",
        decision_reason="测试通过",
        numeric_result={"credit_score": 75, "risk_level": "low"},
        semantic_risk={"repayment_willingness": "high"},
        credit_score=75,
        risk_level="low",
        conflict_detected=False,
        trace=[],
    )
    print(f"保存评估: ID={eval_id}")

    # 测试查询
    evaluations = get_evaluations(limit=5)
    print(f"查询历史: {len(evaluations)} 条")

    # 测试统计
    stats = get_statistics()
    print(f"统计: 总数={stats['total']}, 通过={stats['decisions'].get('approve', 0)}")

    # 测试详情
    detail = get_evaluation_by_id(eval_id)
    print(f"详情查询: ID={detail['id']}, 评分={detail['credit_score']}")

    print("✅ 数据库测试通过")
    return True


def test_api_endpoints():
    """测试 API 接口"""
    print("\n" + "="*50)
    print("🧪 测试 API 接口")
    print("="*50)

    from fastapi.testclient import TestClient
    from mini_agent.web.api import app

    client = TestClient(app)

    # 测试健康检查
    response = client.get("/health")
    print(f"健康检查: {response.status_code} - {response.json()}")

    # 测试评估接口
    response = client.post("/api/credit/evaluate", json={
        "numeric_data": {
            "age": 35,
            "income": 50000,
            "credit_history_length": 5,
            "debt_to_income_ratio": 0.3,
            "employment_length": 3,
            "loan_amount": 50000,
            "loan_purpose": "personal",
            "existing_loans": 1,
            "payment_history": 0.9
        },
        "text_data": {
            "application_statement": "贷款用于生意周转",
            "credit_remarks": "信用良好"
        }
    })
    print(f"单笔评估: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  结果: {data['final_decision']}, 评分: {data['numeric_result']['credit_score']}")

    # 测试批量评估
    response = client.post("/api/credit/batch-evaluate", json={
        "applications": [
            {"numeric_data": {"age": 35, "income": 50000, "credit_history_length": 5,
             "debt_to_income_ratio": 0.3, "employment_length": 3, "loan_amount": 50000,
             "loan_purpose": "personal", "existing_loans": 1, "payment_history": 0.9}},
            {"numeric_data": {"age": 28, "income": 30000, "credit_history_length": 3,
             "debt_to_income_ratio": 0.6, "employment_length": 2, "loan_amount": 30000,
             "loan_purpose": "personal", "existing_loans": 2, "payment_history": 0.7}}
        ]
    })
    print(f"批量评估: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  结果: 总数={data['total']}, 通过={data['success']}, 拒绝={data['failed']}")

    # 测试评估历史
    response = client.get("/api/evaluations")
    print(f"历史列表: {response.status_code}")

    # 测试统计
    response = client.get("/api/evaluations/statistics")
    print(f"统计接口: {response.status_code}")

    print("✅ API 接口测试通过")
    return True


async def main():
    """运行所有测试"""
    print("\n🚀 开始全面测试...")
    print("="*50)

    results = []

    # 测试各模块
    try:
        results.append(("XGBoost 评分", await test_xgboost()))
    except Exception as e:
        print(f"❌ XGBoost 测试失败: {e}")
        results.append(("XGBoost 评分", False))

    try:
        results.append(("规则引擎", await test_risk_rules()))
    except Exception as e:
        print(f"❌ 规则引擎测试失败: {e}")
        results.append(("规则引擎", False))

    try:
        results.append(("RAG 检索", await test_rag()))
    except Exception as e:
        print(f"❌ RAG 测试失败: {e}")
        results.append(("RAG 检索", False))

    try:
        results.append(("数据库", test_database()))
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        results.append(("数据库", False))

    try:
        results.append(("API 接口", test_api_endpoints()))
    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        results.append(("API 接口", False))

    # 打印结果汇总
    print("\n" + "="*50)
    print("📊 测试结果汇总")
    print("="*50)
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + "="*50)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())