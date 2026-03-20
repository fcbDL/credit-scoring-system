#!/usr/bin/env python3
"""
AUC 对比测试：XGBoost vs 逻辑回归
用于验证开题指标：XGBoost 的 AUC 应显著优于逻辑回归
"""

import json
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 配置
DATA_PATH = "data/GiveMeSomeCredit/cs-training.csv"
MODEL_PATH = "data/GiveMeSomeCredit/credit_model.json"

def load_data():
    """加载并预处理数据"""
    print("📂 加载数据...")
    df = pd.read_csv(DATA_PATH)

    # 预处理
    df = df.dropna()  # 删除缺失值

    # 特征列（与 GiveMeSomeCredit 一致）
    feature_cols = [
        'RevolvingUtilizationOfUnsecuredLines',
        'age',
        'NumberOfTime30-59DaysPastDueNotWorse',
        'DebtRatio',
        'MonthlyIncome',
        'NumberOfOpenCreditLinesAndLoans',
        'NumberOfTimes90DaysLate',
        'NumberRealEstateLoansOrLines',
        'NumberOfTime60-89DaysPastDueNotWorse',
        'NumberOfDependents'
    ]

    X = df[feature_cols].values
    y = df['SeriousDlqin2yrs'].values

    print(f"   样本数: {len(y)}, 违约比例: {y.mean():.2%}")
    return X, y


def train_models(X_train, y_train):
    """训练 XGBoost 和逻辑回归模型"""
    print("\n🔧 训练模型...")

    # XGBoost
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    xgb_model.fit(X_train, y_train)
    print("   XGBoost 训练完成")

    # 逻辑回归
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    print("   逻辑回归 训练完成")

    return xgb_model, lr_model


def evaluate_models(xgb_model, lr_model, X_test, y_test):
    """评估模型性能"""
    print("\n📊 模型评估...")

    # 预测概率
    xgb_prob = xgb_model.predict_proba(X_test)[:, 1]
    lr_prob = lr_model.predict_proba(X_test)[:, 1]

    # 计算 AUC
    xgb_auc = roc_auc_score(y_test, xgb_prob)
    lr_auc = roc_auc_score(y_test, lr_prob)

    print(f"\n{'='*50}")
    print(f"🎯 AUC 对比结果")
    print(f"{'='*50}")
    print(f"XGBoost AUC:     {xgb_auc:.4f}")
    print(f"逻辑回归 AUC:    {lr_auc:.4f}")
    print(f"AUC 提升:        {(xgb_auc - lr_auc):.4f} ({(xgb_auc/lr_auc - 1)*100:.1f}%)")

    # 开题指标对比
    print(f"\n{'='*50}")
    print(f"🎯 开题指标对比")
    print(f"{'='*50}")
    if xgb_auc > lr_auc:
        print(f"✅ XGBoost AUC > 逻辑回归 AUC: 达标")
    else:
        print(f"❌ XGBoost AUC ≤ 逻辑回归 AUC: 未达标")

    # 保存结果
    result = {
        "xgb_auc": xgb_auc,
        "lr_auc": lr_auc,
        "improvement": xgb_auc - lr_auc,
        "improvement_percent": (xgb_auc/lr_auc - 1)*100,
        "test_samples": len(y_test)
    }

    with open("data/auc_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n📄 结果已保存至: data/auc_results.json")

    return result


def main():
    print("="*50)
    print("📊 XGBoost vs 逻辑回归 AUC 对比测试")
    print("="*50)

    # 加载数据
    X, y = load_data()

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   训练集: {len(y_train)}, 测试集: {len(y_test)}")

    # 训练模型
    xgb_model, lr_model = train_models(X_train, y_train)

    # 评估
    result = evaluate_models(xgb_model, lr_model, X_test, y_test)

    return result


if __name__ == "__main__":
    main()
