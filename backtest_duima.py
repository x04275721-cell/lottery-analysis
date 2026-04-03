#!/usr/bin/env python3
"""
对码法回测 - 验证准确率
"""

import json
from collections import Counter

# 对码表: 0-5, 1-6, 2-7, 3-8, 4-9
DUIMA_PAIRS = {
    '0': '5', '5': '0',
    '1': '6', '6': '1',
    '2': '7', '7': '2',
    '3': '8', '8': '3',
    '4': '9', '9': '4'
}

def get_duima_group(last_num):
    """
    获取对码分解组
    last_num: 上期奖号，如 "048"
    返回: (对码组6个数字, 剩余组4个数字)
    """
    duima_set = set()
    for digit in last_num:
        duima_set.add(digit)
        duima_set.add(DUIMA_PAIRS[digit])

    duima_group = sorted(duima_set)
    all_digits = set('0123456789')
    remaining_group = sorted(all_digits - duima_set)

    return ''.join(duima_group), ''.join(remaining_group)

def check_hit(result_num, last_num):
    """
    检查分解式预判是否正确
    规则：
    - 正确：两边都有号（1+2、2+1、1+1[组三]）
    - 错误：只有一边有号（3+0、0+3、2+0、0+2[组三]）

    注意：组三要看不同数字的分布，不是出现次数
    """
    duima_group, remaining_group = get_duima_group(last_num)

    # 获取开奖号中的不同数字
    unique_digits = set(result_num)

    # 统计不同数字在两组中的分布
    unique_in_duima = sum(1 for d in unique_digits if d in duima_group)
    unique_in_remaining = sum(1 for d in unique_digits if d in remaining_group)

    # 正确：两边都有号
    if unique_in_duima >= 1 and unique_in_remaining >= 1:
        return True, f"{unique_in_duima}+{unique_in_remaining}"

    # 错误：只有一边有号
    return False, f"{unique_in_duima}+{unique_in_remaining}"

def backtest(data, name, periods=100):
    """
    回测对码法
    规则：分解式预判正确 = 两边都有号（1+2 或 2+1）
         分解式预判错误 = 只有一边有号（3+0 或 0+3）
    data: 排好序的数据（最新在前）
    name: 名称
    periods: 回测期数
    """
    print(f"\n{'='*50}")
    print(f"  {name} 对码法回测 (最近{periods}期)")
    print(f"{'='*50}")

    # 取最新期开始，往前回测periods期
    test_data = data[:periods+1]  # 多取1期作为起始

    total = 0  # 总预测次数
    correct_count = 0  # 正确次数

    # 分布统计
    distribution_stats = {'1+2': 0, '2+1': 0, '3+0': 0, '0+3': 0}

    for i in range(len(test_data) - 1):
        # 上期号码（用来生成对码）
        last_num = test_data[i+1]['number']
        # 本期实际开奖号码
        result_num = test_data[i]['number']

        # 检查分解式预判是否正确（两边都有号=正确）
        is_correct, distribution = check_hit(result_num, last_num)

        if is_correct:
            correct_count += 1
        total += 1

        # 统计分布
        if distribution in distribution_stats:
            distribution_stats[distribution] += 1

    correct_rate = correct_count / total * 100 if total > 0 else 0

    print(f"总预测次数: {total}")
    print(f"正确次数: {correct_count}")
    print(f"正确率: {correct_rate:.2f}%")

    print(f"\n分布统计:")
    for dist, count in sorted(distribution_stats.items()):
        pct = count / total * 100 if total > 0 else 0
        print(f"  {dist}: {count}次 ({pct:.1f}%)")

    return {
        'total': total,
        'correct_count': correct_count,
        'correct_rate': correct_rate,
        'distribution': distribution_stats
    }

def backtest_with_predictions(data, name, periods=20):
    """
    回测并显示详细预测结果
    规则：两边都有号（1+2 或 2+1）= 正确
         只有一边有号（3+0 或 0+3）= 错误
    """
    print(f"\n{'='*50}")
    print(f"  {name} 对码法详细回测 (最近{periods}期)")
    print(f"{'='*50}")
    print(f"{'期号':<10} {'上期':<8} {'对码组':<10} {'剩余组':<8} {'开奖':<8} {'命中':<5} {'结果'}")
    print('-'*70)

    test_data = data[:periods+1]

    correct_count = 0

    for i in range(len(test_data) - 1):
        period = test_data[i]['period']
        last_num = test_data[i+1]['number']
        result_num = test_data[i]['number']

        duima_group, remaining_group = get_duima_group(last_num)

        is_correct, distribution = check_hit(result_num, last_num)

        if is_correct:
            correct_count += 1

        status = "[OK]" if is_correct else "[X]"

        print(f"{period:<10} {last_num:<8} {duima_group:<10} {remaining_group:<8} {result_num:<8} {distribution}   {status}")

    total = len(test_data) - 1
    print('-'*70)
    print(f"正确: {correct_count}/{total} = {correct_count/total*100:.1f}%")
    print(f"错误: {total-correct_count}/{total} = {(total-correct_count)/total*100:.1f}%")

if __name__ == '__main__':
    # 读取数据
    with open('c:/Users/zhao/WorkBuddy/Claw/data/all_history.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 分离并排序（降序，最新在前）
    data_3d = sorted([d for d in data if d['type'] == '3d'], key=lambda x: x['period'], reverse=True)
    data_pl3 = sorted([d for d in data if d['type'] == 'pl3'], key=lambda x: x['period'], reverse=True)

    print(f"\n数据概览:")
    print(f"3D: {len(data_3d)}条, 最新期号 {data_3d[0]['period']}")
    print(f"排列三: {len(data_pl3)}条, 最新期号 {data_pl3[0]['period']}")

    # 回测100期
    backtest(data_3d, '3D', 100)
    backtest(data_pl3, '排列三', 100)

    # 详细回测20期看具体结果
    backtest_with_predictions(data_3d, '3D', 20)
    backtest_with_predictions(data_pl3, '排列三', 20)