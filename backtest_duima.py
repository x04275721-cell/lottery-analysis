#!/usr/bin/env python3
"""
分解式回测 - 验证对码法与和值尾四六分解的准确率

规则：两边都有不同数字 = 正确，只有一边有 = 错误
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

# 和值尾四六分解表
SUM_TAIL_DECOMPOSE = {
    '0': {'4_group': '0126', '6_group': '345789'},
    '5': {'4_group': '0126', '6_group': '345789'},
    '1': {'4_group': '1237', '6_group': '045689'},
    '6': {'4_group': '1237', '6_group': '045689'},
    '2': {'4_group': '2348', '6_group': '015679'},
    '7': {'4_group': '2348', '6_group': '015679'},
    '3': {'4_group': '3459', '6_group': '012678'},
    '8': {'4_group': '3459', '6_group': '012678'},
    '4': {'4_group': '0456', '6_group': '123789'},
    '9': {'4_group': '0456', '6_group': '123789'},
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

    duima_group = ''.join(sorted(duima_set))
    remaining_group = ''.join(sorted(set('0123456789') - duima_set))

    return duima_group, remaining_group


def get_sum_tail_group(last_num):
    """
    获取和值尾四六分解组
    last_num: 上期奖号，如 "048"
    返回: (4码组, 6码组, 和值尾)
    """
    sum_val = sum(int(d) for d in last_num)
    sum_tail = str(sum_val % 10)
    decompose = SUM_TAIL_DECOMPOSE[sum_tail]
    return decompose['4_group'], decompose['6_group'], sum_tail


def check_result(result_num, group_a, group_b):
    """
    检查分解式预判是否正确（通用函数）

    规则：两边都有不同数字 = 正确，只有一边有 = 错误
    """
    unique_digits = set(result_num)
    in_a = sum(1 for d in unique_digits if d in group_a)
    in_b = sum(1 for d in unique_digits if d in group_b)
    distribution = f"{in_a}+{in_b}"

    if in_a >= 1 and in_b >= 1:
        return True, distribution
    return False, distribution


def check_duima(result_num, last_num):
    """对码法检查"""
    group_a, group_b = get_duima_group(last_num)
    return check_result(result_num, group_a, group_b)


def check_sum_tail(result_num, last_num):
    """和值尾四六分解检查"""
    group_a, group_b, _ = get_sum_tail_group(last_num)
    return check_result(result_num, group_a, group_b)


def get_combined_groups(last_num):
    """
    获取组合分解组：同时使用对码法与和值尾四六分解

    返回: (对码组, 剩余组, 4码组, 6码组, 交集)
    交集 = 对码组 ∩ 4码组（两边都有的号码）
    """
    duima_group, remaining_group = get_duima_group(last_num)
    group4, group6, sum_tail = get_sum_tail_group(last_num)

    # 交集：两边都有的号码
    intersection = ''.join(sorted(set(duima_group) & set(group4)))

    return duima_group, remaining_group, group4, group6, intersection


def get_combined_intersection(last_num):
    """
    获取组合使用的杀号
    取两套分解的【4码组】和【对码组】的交集作为杀号条件
    """
    duima_group, _ = get_duima_group(last_num)
    group4, _, _ = get_sum_tail_group(last_num)

    # 交集：两边都有的号码（可作为杀号参考）
    return ''.join(sorted(set(duima_group) & set(group4)))


def backtest_combined(data, name, periods=100):
    """
    回测组合分解式（同时使用两种方法）
    测试多种组合规则
    """
    test_data = data[:periods+1]

    # 统计各种情况
    both_correct = 0  # 两种都正确
    both_wrong = 0   # 两种都错误
    one_correct = 0  # 只有一种正确
    duima_only = 0   # 只有对码法正确
    sumtail_only = 0  # 只有和值尾正确

    for i in range(len(test_data) - 1):
        last_num = test_data[i+1]['number']
        result_num = test_data[i]['number']

        is_correct_duima, _ = check_duima(result_num, last_num)
        is_correct_sum_tail, _ = check_sum_tail(result_num, last_num)

        if is_correct_duima and is_correct_sum_tail:
            both_correct += 1
        elif not is_correct_duima and not is_correct_sum_tail:
            both_wrong += 1
        else:
            one_correct += 1
            if is_correct_duima:
                duima_only += 1
            else:
                sumtail_only += 1

    total = both_correct + both_wrong + one_correct

    print(f"\n{'='*60}")
    print(f"  {name} 组合分解式回测 (最近{periods}期)")
    print(f"{'='*60}")
    print(f"\n原始统计:")
    print(f"  两种都正确: {both_correct}次 ({both_correct/total*100:.1f}%)")
    print(f"  两种都错误: {both_wrong}次 ({both_wrong/total*100:.1f}%)")
    print(f"  只有一种正确: {one_correct}次 ({one_correct/total*100:.1f}%)")
    print(f"    - 只有对码法正确: {duima_only}次")
    print(f"    - 只有和值尾正确: {sumtail_only}次")

    print(f"\n组合规则对比:")
    print(f"  规则A - 两种都正确才算正确: {both_correct}/{total} = {both_correct/total*100:.1f}%")
    print(f"  规则B - 任一正确即正确: {total-both_wrong}/{total} = {(total-both_wrong)/total*100:.1f}%")
    print(f"  规则C - 两种都错才算错（任一正确=正确）: {(both_correct+one_correct)}/{total} = {(both_correct+one_correct)/total*100:.1f}%")

    # 规则D：选择正确率更高的那种方法
    duima_count = both_correct + duima_only
    sumtail_count = both_correct + sumtail_only
    print(f"  规则D - 选择正确率更高的方法:")
    print(f"    对码法贡献: {duima_count}/{total} = {duima_count/total*100:.1f}%")
    print(f"    和值尾贡献: {sumtail_count}/{total} = {sumtail_count/total*100:.1f}%")

    return {
        'total': total,
        'both_correct': both_correct,
        'both_wrong': both_wrong,
        'one_correct': one_correct,
        'duima_only': duima_only,
        'sumtail_only': sumtail_only
    }


def check_stability(data, periods=30):
    """
    检查方法的稳定度（最近30期）
    稳定标准：>=85%（30期里最多4-5期出现"单边出3"的情况）
    返回: (正确率, 是否稳定)
    """
    test_data = data[:periods+1]

    total = 0
    correct_count = 0

    for i in range(len(test_data) - 1):
        last_num = test_data[i+1]['number']
        result_num = test_data[i]['number']

        is_correct_duima, _ = check_duima(result_num, last_num)
        is_correct_sum_tail, _ = check_sum_tail(result_num, last_num)

        # 两种方法都正确才算本期稳定
        if is_correct_duima and is_correct_sum_tail:
            correct_count += 1
        total += 1

    correct_rate = correct_count / total * 100 if total > 0 else 0
    is_stable = correct_rate >= 85

    return correct_rate, is_stable, correct_count, total


def get_stability_warning(data_3d, data_pl3, periods=30):
    """
    获取稳定度警告信息
    """
    duima_rate, duima_stable, duima_correct, duima_total = check_stability(data_3d, periods)
    # ... similar for pl3

    warnings = []

    # 3D警告
    if not duima_stable:
        warnings.append(f"【3D】近期正确率 {duima_rate:.1f}%（{duima_correct}/{duima_total}），低于85%稳定线，谨慎使用")

    return warnings


def backtest(data, name, periods=100, method='duima'):
    """
    回测分解式
    data: 排好序的数据（最新在前）
    name: 名称
    periods: 回测期数
    method: 'duima' 或 'sum_tail'
    """
    check_func = check_duima if method == 'duima' else check_sum_tail
    method_name = '对码法' if method == 'duima' else '和值尾四六分解'

    print(f"\n{'='*50}")
    print(f"  {name} {method_name}回测 (最近{periods}期)")
    print(f"{'='*50}")

    test_data = data[:periods+1]

    total = 0
    correct_count = 0
    distribution_stats = {'1+1': 0, '1+2': 0, '2+1': 0, '3+0': 0, '0+3': 0, '2+0': 0, '0+2': 0}

    for i in range(len(test_data) - 1):
        last_num = test_data[i+1]['number']
        result_num = test_data[i]['number']

        is_correct, distribution = check_func(result_num, last_num)

        if is_correct:
            correct_count += 1
        total += 1

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


def backtest_both(data, name, periods=100):
    """同时回测两种方法"""
    print(f"\n{'='*60}")
    print(f"  {name} 两种分解式回测 (最近{periods}期)")
    print(f"{'='*60}")

    r1 = backtest(data, name, periods, 'duima')
    r2 = backtest(data, name, periods, 'sum_tail')

    print(f"\n{'='*60}")
    print(f"  {name} 对比结果")
    print(f"{'='*60}")
    print(f"  对码法正确率:     {r1['correct_rate']:.2f}%")
    print(f"  和值尾四六分解:   {r2['correct_rate']:.2f}%")

    return r1, r2


def backtest_detail(data, name, periods=20, method='duima'):
    """详细回测（显示每期结果）"""
    check_func = check_duima if method == 'duima' else check_sum_tail
    method_name = '对码法' if method == 'duima' else '和值尾四六分解'
    group_name_a = '对码组' if method == 'duima' else '4码组'
    group_name_b = '剩余组' if method == 'duima' else '6码组'

    print(f"\n{'='*60}")
    print(f"  {name} {method_name}详细回测 (最近{periods}期)")
    print(f"{'='*60}")

    test_data = data[:periods+1]

    correct_count = 0

    print(f"{'期号':<10} {'上期':<8} {group_name_a:<10} {group_name_b:<8} {'开奖':<8} {'分布':<6} {'结果'}")
    print('-' * 70)

    for i in range(len(test_data) - 1):
        period = test_data[i]['period']
        last_num = test_data[i+1]['number']
        result_num = test_data[i]['number']

        if method == 'duima':
            group_a, group_b = get_duima_group(last_num)
        else:
            group_a, group_b, sum_tail = get_sum_tail_group(last_num)

        is_correct, distribution = check_func(result_num, last_num)

        if is_correct:
            correct_count += 1

        status = "[OK]" if is_correct else "[X]"

        print(f"{period:<10} {last_num:<8} {group_a:<10} {group_b:<8} {result_num:<8} {distribution:<6} {status}")

    total = len(test_data) - 1
    print('-' * 70)
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

    # =========================================
    # 1. 单独回测100期
    # =========================================
    backtest_both(data_3d, '3D', 100)
    backtest_both(data_pl3, '排列三', 100)

    # =========================================
    # 2. 组合回测100期（两种方法都正确才算正确）
    # =========================================
    backtest_combined(data_3d, '3D', 100)
    backtest_combined(data_pl3, '排列三', 100)

    # =========================================
    # 3. 稳定度检查（最近30期）
    # =========================================
    print(f"\n{'='*60}")
    print(f"  稳定度检查 (最近30期)")
    print(f"  标准：两种方法都正确的比例 >=85% 视为稳定")
    print(f"{'='*60}")

    for name, history in [('3D', data_3d), ('排列三', data_pl3)]:
        rate, is_stable, correct, total = check_stability(history, 30)

        print(f"\n【{name}】")
        print(f"  正确率: {rate:.1f}% ({correct}/{total})")

        if is_stable:
            print(f"  状态: [OK] 稳定，可放心使用")
        else:
            print(f"  状态: [WARN] 近期不太稳定，谨慎使用")

    # =========================================
    # 4. 详细回测20期
    # =========================================
    backtest_detail(data_3d, '3D', 20, 'duima')
    backtest_detail(data_pl3, '排列三', 20, 'duima')
    backtest_detail(data_3d, '3D', 20, 'sum_tail')
    backtest_detail(data_pl3, '排列三', 20, 'sum_tail')