#!/usr/bin/env python3
"""
从 GiveMeSomeCredit 数据集生成 LoRA 微调数据
用于训练模型理解信贷评分逻辑
"""

import pandas as pd
import random
import json

# 配置
INPUT_FILE = "data/GiveMeSomeCredit/cs-training.csv"
OUTPUT_FILE = "data/finetune/lora_data.json"
SAMPLE_COUNT = 500  # 生成 500 条数据

# 读取数据
print("📂 加载数据...")
df = pd.read_csv(INPUT_FILE)
df = df.dropna()  # 删除缺失值

# 分层采样：确保正负样本均衡
df_normal = df[df['SeriousDlqin2yrs'] == 0].sample(n=250, random_state=42)
df_default = df[df['SeriousDlqin2yrs'] == 1].sample(n=250, random_state=42)
df_sample = pd.concat([df_normal, df_default]).sample(frac=1, random_state=42)

# 特征列名映射到中文
FEATURE_MAP = {
    'RevolvingUtilizationOfUnsecuredLines': '循环信用利用率',
    'age': '年龄',
    'NumberOfTime30-59DaysPastDueNotWorse': '30-59天逾期次数',
    'DebtRatio': '负债率',
    'MonthlyIncome': '月收入',
    'NumberOfOpenCreditLinesAndLoans': '信用账户数量',
    'NumberOfTimes90DaysLate': '90天以上逾期次数',
    'NumberRealEstateLoansOrLines': '房贷数量',
    'NumberOfTime60-89DaysPastDueNotWorse': '60-89天逾期次数',
    'NumberOfDependents': '家属人数',
}


def generate_description(row):
    """将数值特征转换为自然语言描述"""
    parts = []

    # 年龄
    age = row['age']
    if age < 25:
        age_desc = "年轻客户"
    elif age < 35:
        age_desc = "青年客户"
    elif age < 50:
        age_desc = "中年客户"
    else:
        age_desc = "中老年客户"
    parts.append(f"年龄{age}岁({age_desc})")

    # 收入
    income = row['MonthlyIncome']
    if income < 3000:
        income_desc = "较低"
    elif income < 6000:
        income_desc = "中等"
    elif income < 10000:
        income_desc = "较高"
    else:
        income_desc = "高收入"
    parts.append(f"月收入{income:.0f}元({income_desc})")

    # 负债率
    debt_ratio = row['DebtRatio']
    if debt_ratio < 0.3:
        debt_desc = "低"
    elif debt_ratio < 0.5:
        debt_desc = "中等"
    else:
        debt_desc = "高"
    parts.append(f"负债率{debt_ratio:.1%}({debt_desc})")

    # 逾期情况
    late_30_59 = row['NumberOfTime30-59DaysPastDueNotWorse']
    late_60_89 = row['NumberOfTime60-89DaysPastDueNotWorse']
    late_90 = row['NumberOfTimes90DaysLate']
    total_late = late_30_59 + late_60_89 + late_90

    if total_late == 0:
        late_desc = "无逾期记录"
    elif total_late <= 2:
        late_desc = "偶尔逾期"
    else:
        late_desc = f"多次逾期(共{total_late}次)"
    parts.append(late_desc)

    # 信用账户
    credit_count = row['NumberOfOpenCreditLinesAndLoans']
    parts.append(f"拥有{credit_count}个信用账户")

    # 房贷
    estate_count = row['NumberRealEstateLoansOrLines']
    if estate_count > 0:
        parts.append(f"有{estate_count}笔房贷")

    # 家属
    dependents = row['NumberOfDependents']
    parts.append(f"家庭成员{dependents}人")

    return "，".join(parts)


def generate_instruction(row):
    """生成指令和期望输出"""
    # 真实标签：1=违约，0=正常
    label = row['SeriousDlqin2yrs']

    # 构建描述
    desc = generate_description(row)

    # 生成指令
    instruction = "请分析以下贷款申请人的信用风险，并给出评估结果。"

    # 生成输入
    input_text = f"申请人信息：{desc}"

    # 生成输出（工具调用逻辑）
    if label == 0:
        # 正常客户
        output = f"""根据分析：
1. 调用 XGBoost 评分工具进行数值评估
2. 该申请人信用评分较高，违约概率低
3. 数值评分结果：建议通过
4. 风险等级：低风险
5. 最终决策：通过"""

        decision = "通过"
    else:
        # 违约客户
        output = f"""根据分析：
1. 调用 XGBoost 评分工具进行数值评估
2. 该申请人存在逾期记录，信用评分较低
3. 数值评分结果：建议拒绝
4. 风险等级：高风险
5. 最终决策：拒绝"""

        decision = "拒绝"

    return {
        "instruction": instruction,
        "input": input_text,
        "output": output,
        "label": int(label),
        "decision": decision
    }


# 生成数据
print(f"🔧 生成 {SAMPLE_COUNT} 条微调数据...")
data_list = []

for idx, row in df_sample.iterrows():
    item = generate_instruction(row)
    data_list.append(item)

    if len(data_list) % 50 == 0:
        print(f"   已生成 {len(data_list)} 条...")

# 保存
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data_list, f, ensure_ascii=False, indent=2)

# 统计
label_0 = sum(1 for d in data_list if d['label'] == 0)
label_1 = sum(1 for d in data_list if d['label'] == 1)

print(f"\n✅ 完成！已保存至: {OUTPUT_FILE}")
print(f"   总数量: {len(data_list)}")
print(f"   正常(0): {label_0}")
print(f"   违约(1): {label_1}")
