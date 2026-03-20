#!/usr/bin/env python3
"""
数据映射脚本：将 GiveMeSomeCredit 数据转换为信贷评分系统输入格式
"""

import pandas as pd
import numpy as np
import random
import json

# 读取数据
df = pd.read_csv("data/GiveMeSomeCredit/cs-training.csv", index_col=0)

# 字段映射说明：
# GiveMeSomeCredit 字段 -> 我们的系统字段
# SeriousDlqin2yrs -> 目标标签（1=违约，0=正常）
# age -> age
# MonthlyIncome -> income (转换为年收入)
# DebtRatio -> debt_to_income_ratio
# RevolvingUtilizationOfUnsecuredLines -> 可作为信用利用率
# NumberOfTime30-59DaysPastDueNotWorse -> 逾期次数
# NumberOfTime60-89DaysPastDueNotWorse -> 逾期次数
# NumberOfTimes90DaysLate -> 逾期次数
# NumberOfOpenCreditLinesAndLoans -> existing_loans
# NumberRealEstateLoansOrLines -> 房贷数量

def convert_row(row):
    """将一行 GiveMeSomeCredit 数据转换为系统输入格式"""

    # 年收入：直接使用或处理缺失值
    income = row.get("MonthlyIncome", 50000)
    if pd.isna(income) or income <= 0:
        income = 50000  # 默认收入

    # 年龄
    age = int(row.get("age", 30))
    if pd.isna(age) or age < 18:
        age = 30

    # 负债率
    debt_ratio = row.get("DebtRatio", 0.3)
    if pd.isna(debt_ratio):
        debt_ratio = 0.3
    debt_ratio = min(max(debt_ratio, 0), 1)  # 限制在 0-1

    # 现有贷款数
    existing_loans = int(row.get("NumberOfOpenCreditLinesAndLoans", 1))
    if pd.isna(existing_loans):
        existing_loans = 1

    # 逾期次数转换为 payment_history (0-1，越高越好)
    late_30_59 = row.get("NumberOfTime30-59DaysPastDueNotWorse", 0)
    late_60_89 = row.get("NumberOfTime60-89DaysPastDueNotWorse", 0)
    late_90 = row.get("NumberOfTimes90DaysLate", 0)

    if pd.isna(late_30_59): late_30_59 = 0
    if pd.isna(late_60_89): late_60_89 = 0
    if pd.isna(late_90): late_90 = 0

    # 限制异常值：逾期次数最多计算 10 次（超过 10 次按 10 次处理）
    total_late = min(10, late_30_59 + late_60_89 + late_90)

    # 计算 payment_history (基于逾期次数)
    payment_history = max(0, 1 - total_late / 10)
    payment_history = round(payment_history, 2)

    # 模拟字段（原始数据没有，需要生成）
    # 贷款金额：基于收入的 1-5 倍
    loan_amount = int(income * random.uniform(0.5, 3))

    # 贷款用途：随机分配
    purposes = ["personal", "personal", "personal", "home_improvement", "business", "education"]
    loan_purpose = random.choice(purposes)

    # 信用历史长度：基于年龄，假设 18 岁开始有信用记录
    credit_history_length = max(1, age - 18)
    if pd.notna(row.get("NumberOfTimes90DaysLate")) and row.get("NumberOfTimes90DaysLate", 0) > 0:
        credit_history_length = max(1, credit_history_length - 2)  # 严重逾期可能缩短历史

    # 工作年限：基于年龄，假设 22 岁开始工作
    employment_length = max(0, age - 22)

    # 生成申请文本（基于数据特征和标签）
    if row.get("SeriousDlqin2yrs") == 1:
        # 违约用户 - 模拟有风险的申请
        # 特点：信息不完整、描述模糊、可能有多次逾期
        statements = [
            "我需要一笔钱周转，短期就可以还",
            "贷款用于生意资金周转",
            "急需用钱，麻烦快一点",
            "之前在其他平台借过钱",
            "贷款用于还债",
            "我需要钱，具体用途不便透露",
            "申请贷款10万急用",
        ]
        # 违约用户如果有多次逾期，文本中体现
        if total_late > 0:
            statements.append(f"之前有{total_late}次逾期，现在需要资金周转")
    else:
        # 正常用户 - 模拟真实、详细的申请
        # 特点：信息完整、用处明确、有稳定收入和良好信用
        statements = [
            "我需要贷款50万元用于房屋装修，已签订装修合同，工程预算30万元，自有资金10万元，贷款期限3年，有稳定收入。",
            "申请个人消费贷款30万元，用于购买家电家具，有稳定工作和社保，信用记录良好。",
            "用于个人综合消费支出，有房产作为保障，收入稳定，准备好了收入证明。",
            "贷款用于购买一辆汽车，已选中车型，裸车价25万元，自有资金5万元，贷款20万元。",
            "申请经营贷款100万元用于店铺扩大经营，有营业执照和实体店，流水良好。",
            "贷款用于教育培训，提升技能，有还款计划。",
            "申请房屋装修贷款20万元，已签订装修合同，工程预算25万元，自有资金5万元。",
        ]
        # 正常用户强调信用良好
        if payment_history >= 0.95:
            statements.append("个人信用记录良好，从未逾期，本次贷款用途明确，还款来源稳定。")

    application_statement = random.choice(statements)

    # 征信备注（使用原始 total_late，但最多显示 10 次）
    display_late = min(10, late_30_59 + late_60_89 + late_90)
    if display_late > 0:
        credit_remarks = f"有{display_late}次逾期记录"
    else:
        credit_remarks = "信用良好，无逾期记录"

    return {
        "numeric_data": {
            "age": age,
            "income": int(income),
            "credit_history_length": credit_history_length,
            "debt_to_income_ratio": round(debt_ratio, 4),
            "employment_length": employment_length,
            "loan_amount": loan_amount,
            "loan_purpose": loan_purpose,
            "existing_loans": existing_loans,
            "payment_history": payment_history,
        },
        "text_data": {
            "application_statement": application_statement,
            "credit_remarks": credit_remarks,
        },
        "label": int(row.get("SeriousDlqin2yrs", 0)),  # 真实标签
    }


def generate_test_data(n_samples=100, output_file="data/test_samples.json"):
    """
    生成测试数据集

    Args:
        n_samples: 生成的样本数量
        output_file: 输出文件路径
    """

    # 采样：确保正负样本比例均衡（1:1），方便测试
    n_positive = n_samples // 2  # 违约样本
    n_negative = n_samples - n_positive  # 正常样本

    # 优先使用有逾期记录的违约样本
    df_positive_all = df[df["SeriousDlqin2yrs"] == 1]
    df_positive = df_positive_all.sample(n=min(n_positive, len(df_positive_all)), random_state=42)

    # 正常样本
    df_negative_all = df[df["SeriousDlqin2yrs"] == 0]
    df_negative = df_negative_all.sample(n=min(n_negative, len(df_negative_all)), random_state=42)

    df_sample = pd.concat([df_positive, df_negative]).sample(frac=1, random_state=42).head(n_samples)

    # 转换
    test_data = []
    for idx, row in df_sample.iterrows():
        converted = convert_row(row)
        test_data.append(converted)

    # 保存
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 生成 {len(test_data)} 条测试数据")
    print(f"   正样本(违约): {sum(1 for d in test_data if d['label']==1)}")
    print(f"   负样本(正常): {sum(1 for d in test_data if d['label']==0)}")
    print(f"   保存至: {output_file}")

    return test_data


if __name__ == "__main__":
    import sys
    import os

    # 确保在项目根目录运行
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    generate_test_data(n_samples=n)
