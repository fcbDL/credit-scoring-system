import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

def train_credit_model():
    # 1. 动态获取路径：确保在任何环境下运行都能找到数据
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'cs-training.csv')
    
    if not os.path.exists(data_path):
        print(f"❌ 错误：找不到数据文件 {data_path}")
        return

    # 2. 加载数据 (index_col=0 避开第一列无用 ID)
    print("📅 正在加载并清洗数据...")
    train_df = pd.read_csv(data_path, index_col=0)

    # 3. 极简清洗：处理缺失值
    # 月收入用中位数填补，家属人数填 0
    train_df['MonthlyIncome'] = train_df['MonthlyIncome'].fillna(train_df['MonthlyIncome'].median())
    train_df['NumberOfDependents'] = train_df['NumberOfDependents'].fillna(0)

    # 4. 准备训练集与验证集
    X = train_df.drop('SeriousDlqin2yrs', axis=1)
    y = train_df['SeriousDlqin2yrs']
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # 5. 配置并训练模型
    print("🚀 正在训练 XGBoost 基准模型...")
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        scale_pos_weight=10,  # 针对不平衡样本的权重优化
        eval_metric='auc',
        random_state=42
    )
    model.fit(X_train, y_train)

    # 6. 评估结果
    pred_prob = model.predict_proba(X_val)[:, 1]
    auc_score = roc_auc_score(y_val, pred_prob)
    print("-" * 30)
    print(f"✅ 训练完成！当前模型验证集 AUC: {auc_score:.4f}")
    print("-" * 30)

    # 7. 打印特征重要性 (论文加分项：分析模型到底在看什么)
    print("\n📊 特征重要性排名（Top 5）：")
    importance = pd.DataFrame({
        'Feature': X.columns,
        'Importance': model.feature_importances_
    }).sort_values(by='Importance', ascending=False)
    print(importance.head(5))

    # 8. 保存模型文件 (供后续 Numeric Agent 调用)
    model_path = os.path.join(script_dir, 'credit_model.json')
    model.save_model(model_path)
    print(f"\n💾 模型已保存至: {model_path}")

if __name__ == "__main__":
    train_credit_model()