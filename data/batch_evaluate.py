#!/usr/bin/env python3
"""
批量评估脚本：测试信贷评分系统的性能
"""

import requests
import json
import time
from collections import defaultdict

API_URL = "http://localhost:8000/api/credit/evaluate"

def load_test_data(file_path="data/test_samples.json"):
    """加载测试数据"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_single(data):
    """调用 API 评估单条数据"""
    try:
        response = requests.post(
            API_URL,
            json={
                "numeric_data": data["numeric_data"],
                "text_data": data["text_data"]
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API 错误: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def map_decision_to_label(decision):
    """将决策结果映射为二分类标签"""
    # decision: approve=通过, reject=拒绝, review=待定
    if decision == "approve":
        return 0  # 正常
    elif decision == "reject":
        return 1  # 违约
    else:  # review
        return -1  # 待定


def calculate_metrics(y_true, y_pred):
    """计算评估指标"""
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

    # 过滤掉 -1（待定）
    valid_idx = [i for i, y in enumerate(y_pred) if y != -1]
    if len(valid_idx) == 0:
        return None

    y_true_filtered = [y_true[i] for i in valid_idx]
    y_pred_filtered = [y_pred[i] for i in valid_idx]

    accuracy = accuracy_score(y_true_filtered, y_pred_filtered)
    precision = precision_score(y_true_filtered, y_pred_filtered, zero_division=0)
    recall = recall_score(y_true_filtered, y_pred_filtered, zero_division=0)
    f1 = f1_score(y_true_filtered, y_pred_filtered, zero_division=0)
    cm = confusion_matrix(y_true_filtered, y_pred_filtered)

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": cm.tolist(),
        "total": len(valid_idx),
        "excluded": len(y_pred) - len(valid_idx)  # 被排除的待定样本
    }


def run_batch_test(n_samples=10, delay=2):
    """批量测试"""
    print("=" * 60)
    print("📊 信贷评分系统批量评估")
    print("=" * 60)

    # 加载测试数据
    test_data = load_test_data()
    if len(test_data) < n_samples:
        n_samples = len(test_data)

    print(f"📂 加载 {n_samples} 条测试数据\n")

    results = []
    y_true = []
    y_pred = []

    for i in range(n_samples):
        data = test_data[i]
        true_label = data["label"]

        print(f"[{i+1}/{n_samples}] 评估中... ", end="")

        result = evaluate_single(data)

        if result:
            decision = result.get("final_decision", "unknown")
            predicted_label = map_decision_to_label(decision)

            results.append({
                "index": i,
                "true_label": true_label,
                "predicted_label": predicted_label,
                "decision": decision,
                "credit_score": result.get("numeric_result", {}).get("credit_score")
            })

            y_true.append(true_label)
            y_pred.append(predicted_label)

            # 打印结果
            status = "✅" if true_label == predicted_label else "❌"
            label_name = "正常" if true_label == 0 else "违约"
            pred_name = {"approve": "通过", "reject": "拒绝", "review": "待定"}.get(decision, decision)
            print(f"{status} 真实:{label_name} → 预测:{pred_name}")
        else:
            print("❌ 失败")

        # 延迟，避免 API 过载
        if i < n_samples - 1:
            time.sleep(delay)

    print("\n" + "=" * 60)
    print("📈 评估结果")
    print("=" * 60)

    # 计算指标
    metrics = calculate_metrics(y_true, y_pred)

    if metrics:
        print(f"\n准确率 (Accuracy): {metrics['accuracy']:.2%}")
        print(f"精确率 (Precision): {metrics['precision']:.2%}")
        print(f"召回率 (Recall): {metrics['recall']:.2%}")
        print(f"F1 分数: {metrics['f1']:.2%}")

        print(f"\n有效样本: {metrics['total']}")
        if metrics['excluded'] > 0:
            print(f"待定样本(排除): {metrics['excluded']}")

        print(f"\n混淆矩阵:")
        cm = metrics['confusion_matrix']
        print(f"              预测正常  预测违约")
        print(f"  实际正常      {cm[0][0]:3d}      {cm[0][1]:3d}")
        print(f"  实际违约      {cm[1][0]:3d}      {cm[1][1]:3d}")

        # 开题指标对比
        print("\n" + "=" * 60)
        print("🎯 开题指标对比")
        print("=" * 60)
        acc_ok = "✅" if metrics['accuracy'] >= 0.85 else "❌"
        f1_ok = "✅" if metrics['f1'] >= 0.80 else "❌"
        print(f"Accuracy ≥ 0.85: {acc_ok} 实际: {metrics['accuracy']:.2%}")
        print(f"F1-score ≥ 0.80: {f1_ok} 实际: {metrics['f1']:.2%}")
    else:
        print("⚠️ 无法计算指标（所有样本都是待定）")

    # 保存详细结果
    output_file = "data/batch_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "results": results,
            "metrics": metrics
        }, f, ensure_ascii=False, indent=2)
    print(f"\n📄 详细结果已保存至: {output_file}")


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    d = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    run_batch_test(n_samples=n, delay=d)
