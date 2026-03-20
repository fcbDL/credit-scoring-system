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

    # 计算 payment_history (基于逾期次数)
    total_late = late_30_59 + late_60_89 + late_90
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

    # 生成申请文本（基于数据特征）
    if row.get("SeriousDlqin2yrs") == 1:
        # 违约用户 - 模拟有风险的申请
        statements = [
            "我需要一笔钱周转，短期就可以还",
            "贷款用于生意资金周转",
            "急需用钱，麻烦快一点",
            "之前在其他平台借过钱",
        ]
    else:
        # 正常用户 - 模拟正常的申请
        statements = [
            "我需要贷款用于房屋装修，已签订装修合同，工程预算30万元，自有资金10万元，贷款期限3年，有稳定收入。",
            "申请个人消费贷款，用于购买家电，有稳定工作收入，信用记录良好。",
            "用于个人消费支出，有房产作为保障，收入稳定。",
        ]

    application_statement = random.choice(statements)

    # 征信备注
    if total_late > 0:
        credit_remarks = f"有{total_late}次逾期记录"
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

    # 采样（保持正负样本比例）
    df_sample = df.sample(n=n_samples, random_state=42)

    # 分别从违约和正常样本中采样，保持原始比例
    positive_ratio = df["SeriousDlqin2yrs"].mean()
    n_positive = int(n_samples * positive_ratio)
    n_negative = n_samples - n_positive

    df_positive = df[df["SeriousDlqin2yrs"] == 1].sample(n=min(n_positive, len(df[df["SeriousDlqin2yrs"] == 1])), random_state=42)
    df_negative = df[df["SeriousDlqin2yrs"] == 0].sample(n=min(n_negative, len(df[df["SeriousDlqin2yrs"] == 0])), random_state=42)

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
