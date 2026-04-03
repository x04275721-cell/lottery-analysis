# -*- coding: utf-8 -*-
"""
彩票分解式预测
包含两种方法：对码法、和值尾四六分解，以及组合使用方法

================================================================================
方法一：对码法（差5对码）
================================================================================

【对码表】
    0 ←→ 5
    1 ←→ 6
    2 ←→ 7
    3 ←→ 8
    4 ←→ 9

【分解方法】
    1. 取上期开奖号码的每一位
    2. 找出每一位的对码（如0→5, 3→8）
    3. 所有对码合并为一个集合（6个数字）
    4. 剩余不在对码组中的4个数字归为剩余组
    5. 格式：对码组(6个) - 剩余组(4个)

    示例：上期奖号 048
        0 → 对码 5
        4 → 对码 9
        8 → 对码 3
        对码集合：{0, 5, 4, 9, 8, 3} → 034589（对码组）
        剩余数字：{1, 2, 6, 7} → 1267（剩余组）
        结果：034589 - 1267

================================================================================
方法二：和值尾四六分解（查表法）
================================================================================

【和值尾对照表】
    和值尾0/5 → 4码组:0126, 6码组:345789
    和值尾1/6 → 4码组:1237, 6码组:045689
    和值尾2/7 → 4码组:2348, 6码组:015679
    和值尾3/8 → 4码组:3459, 6码组:012678
    和值尾4/9 → 4码组:0456, 6码组:123789

【分解方法】
    1. 计算上期奖号的和值
    2. 取和值的尾数（和值 % 10）
    3. 查表得到4码组和6码组

    示例：上期奖号 048
        和值 = 0+4+8 = 12
        和值尾 = 12 % 10 = 2
        查表：和值尾2 → 4码组:2348, 6码组:015679
        结果：2348 - 015679

================================================================================
方法三：组合使用（两种方法结合）
================================================================================

【组合方法】
    不要单吊一套分解。可以同时用"对码法"和"和值尾查表法"，
    取它们的交集（即两边都出现的号码）作为最终条件，安全性更高。

【交集计算】
    交集 = 对码组 ∩ 4码组（两个方法中都出现的号码）

    示例：上期奖号 048
        对码组 = 034589
        和值尾2的4码组 = 2348
        交集 = 034589 ∩ 2348 = 3, 4, 8

【使用建议】
    组合使用时，只有当两种方法都正确时，才算组合正确。
    单一方法错误会导致组合失败。

================================================================================
分解式正确判断规则（两种方法通用）
================================================================================

核心原则：两边都要有不同数字

统计开奖号中不同数字在两组（如对码组/剩余组）的分布：
- 1+2（组三跨两组）：正确
- 2+1（组三跨两组）：正确
- 1+1（组三，两组各一个不同数字）：正确
- 3+0（豹子或三同号，全部在一组）：错误
- 0+3（豹子或三同号，全部在另一组）：错误
- 2+0（组三，两个不同数字都在一组）：错误
- 0+2（组三，两个不同数字都在另一组）：错误

简记：两边都有不同数字 = 正确，只有一边有 = 错误

================================================================================
稳定度判断规则
================================================================================

【判断方法】
    回测最近30期，计算"两种方法都正确"的比例

【判断标准】
    - 正确率 >= 85%：视为稳定，显示"稳定，可放心使用"
    - 正确率 < 85%：显示"近期不太稳定，谨慎使用"

================================================================================
"""

# 对码表：差5对码
DUIMA_PAIRS = {
    '0': '5', '5': '0',
    '1': '6', '6': '1',
    '2': '7', '7': '2',
    '3': '8', '8': '3',
    '4': '9', '9': '4'
}

# 和值尾四六分解表
# 和值尾0/5 → 4码组:0126, 6码组:345789
# 和值尾1/6 → 4码组:1237, 6码组:045689
# 和值尾2/7 → 4码组:2348, 6码组:015679
# 和值尾3/8 → 4码组:3459, 6码组:012678
# 和值尾4/9 → 4码组:0456, 6码组:123789
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


def get_duima_pairs():
    """获取对码对"""
    return DUIMA_PAIRS.copy()


def get_sum_tail_decompose(last_num):
    """
    根据上期奖号计算和值尾四六分解

    参数:
        last_num: 上期开奖号码（字符串，如 "048"）

    返回:
        (4码组字符串, 6码组字符串, 和值尾)
        例如：("0126", "345789", "2")
    """
    # 计算和值
    sum_val = sum(int(d) for d in last_num)
    # 和值尾
    sum_tail = str(sum_val % 10)

    # 查表获取分解
    decompose = SUM_TAIL_DECOMPOSE[sum_tail]
    return decompose['4_group'], decompose['6_group'], sum_tail


def get_duima_group(last_num):
    """
    根据上期奖号生成分解组

    参数:
        last_num: 上期开奖号码（字符串，如 "048"）

    返回:
        (对码组字符串, 剩余组字符串)
        例如：("034589", "1267")
    """
    duima_set = set()

    for digit in last_num:
        duima_set.add(digit)
        duima_set.add(DUIMA_PAIRS[digit])

    # 对码组（6个数字）
    duima_group = ''.join(sorted(duima_set, key=lambda x: int(x)))

    # 剩余组（不在对码组中的4个数字）
    remaining_group = ''.join(sorted(
        [str(i) for i in range(10) if str(i) not in duima_set],
        key=lambda x: int(x)
    ))

    return duima_group, remaining_group


def check_duima_result(result_num, last_num):
    """
    检查对码分解式预判是否正确

    参数:
        result_num: 本期实际开奖号码（字符串，如 "903"）
        last_num: 上期开奖号码（字符串，如 "048"）

    返回:
        (是否正确布尔值, 分布字符串, 说明)
        例如：(True, "2+1", "正确：两边都有不同数字")
    """
    duima_group, remaining_group = get_duima_group(last_num)

    # 获取开奖号中的不同数字
    unique_digits = set(result_num)

    # 统计不同数字在两组中的分布
    in_duima = sum(1 for d in unique_digits if d in duima_group)
    in_remaining = sum(1 for d in unique_digits if d in remaining_group)

    distribution = f"{in_duima}+{in_remaining}"

    # 判断是否正确：两边都有不同数字 = 正确
    if in_duima >= 1 and in_remaining >= 1:
        return True, distribution, "正确：两边都有不同数字"
    else:
        return False, distribution, "错误：只有一边有不同数字"


def check_sum_tail_result(result_num, last_num):
    """
    检查和值尾四六分解式预判是否正确

    参数:
        result_num: 本期实际开奖号码（字符串，如 "903"）
        last_num: 上期开奖号码（字符串，如 "048"）

    返回:
        (是否正确布尔值, 分布字符串, 说明)
    """
    group4, group6, sum_tail = get_sum_tail_decompose(last_num)

    # 获取开奖号中的不同数字
    unique_digits = set(result_num)

    # 统计不同数字在两组中的分布
    in_group4 = sum(1 for d in unique_digits if d in group4)
    in_group6 = sum(1 for d in unique_digits if d in group6)

    distribution = f"{in_group4}+{in_group6}"

    # 判断是否正确：两边都有不同数字 = 正确
    if in_group4 >= 1 and in_group6 >= 1:
        return True, distribution, "正确：两边都有不同数字"
    else:
        return False, distribution, "错误：只有一边有不同数字"


def analyze_duima_method(history_list):
    """
    完整对码分析（用于预测）

    参数:
        history_list: 历史数据列表（最新一期在前）

    返回:
        包含分析结果的字典
    """
    if not history_list or len(history_list[0]['number']) != 3:
        return {
            'last_number': '---',
            'duima_group': '',
            'remaining_group': '',
            'result': '---',
            'rule': '两边都有不同数字 = 正确'
        }

    last_num = history_list[0]['number']
    duima_group, remaining_group = get_duima_group(last_num)

    return {
        'last_number': last_num,
        'duima_group': duima_group,
        'remaining_group': remaining_group,
        'result': f"{duima_group} - {remaining_group}",
        'rule': '两边都有不同数字 = 正确'
    }


def analyze_sum_tail_method(history_list):
    """
    和值尾四六分解分析（用于预测）

    参数:
        history_list: 历史数据列表（最新一期在前）

    返回:
        包含分析结果的字典
    """
    if not history_list or len(history_list[0]['number']) != 3:
        return {
            'last_number': '---',
            'sum_tail': '---',
            'group4': '',
            'group6': '',
            'result': '---',
            'rule': '两边都有不同数字 = 正确'
        }

    last_num = history_list[0]['number']
    group4, group6, sum_tail = get_sum_tail_decompose(last_num)

    return {
        'last_number': last_num,
        'sum_tail': sum_tail,
        'group4': group4,
        'group6': group6,
        'result': f"{group4} - {group6}",
        'rule': '两边都有不同数字 = 正确'
    }


def get_combined_groups(last_num):
    """
    获取组合分解组：同时使用对码法与和值尾四六分解

    参数:
        last_num: 上期开奖号码（字符串，如 "048"）

    返回:
        {
            'duima_group': 对码组,
            'remaining_group': 剩余组,
            'group4': 4码组,
            'group6': 6码组,
            'intersection': 交集（对码组 ∩ 4码组）,
            'sum_tail': 和值尾
        }
    """
    duima_group, remaining_group = get_duima_group(last_num)
    group4, group6, sum_tail = get_sum_tail_decompose(last_num)

    # 交集：两个方法都对码组/4码组中都出现的号码
    intersection = ''.join(sorted(set(duima_group) & set(group4)))

    return {
        'duima_group': duima_group,
        'remaining_group': remaining_group,
        'group4': group4,
        'group6': group6,
        'intersection': intersection,
        'sum_tail': sum_tail
    }


def check_combined_result(result_num, last_num):
    """
    检查组合分解式预判是否正确
    只有当两种方法都正确时，才算组合正确

    返回:
        (是否正确布尔值, 对码法结果, 和值尾结果, 组合结果说明)
    """
    is_correct_duima, dist_duima, _ = check_duima_result(result_num, last_num)
    is_correct_sum_tail, dist_sum_tail, _ = check_sum_tail_result(result_num, last_num)

    is_combined_correct = is_correct_duima and is_correct_sum_tail

    if is_combined_correct:
        msg = "两种都正确"
    elif not is_correct_duima and not is_correct_sum_tail:
        msg = "两种都错误"
    else:
        msg = "只有一种正确"

    return is_combined_correct, (is_correct_duima, dist_duima), (is_correct_sum_tail, dist_sum_tail), msg


def analyze_combined_method(history_list):
    """
    组合分解式分析（用于预测）

    参数:
        history_list: 历史数据列表（最新一期在前）

    返回:
        包含分析结果的字典
    """
    if not history_list or len(history_list[0]['number']) != 3:
        return {
            'last_number': '---',
            'intersection': '---',
            'duima_group': '',
            'group4': '',
            'result': '---',
            'rule': '两边都有不同数字 = 正确'
        }

    last_num = history_list[0]['number']
    combined = get_combined_groups(last_num)

    return {
        'last_number': last_num,
        'intersection': combined['intersection'],
        'duima_group': combined['duima_group'],
        'group4': combined['group4'],
        'result': f"交集: {combined['intersection']}",
        'rule': '两边都有不同数字 = 正确'
    }


def check_stability_single(history_list, method, periods=30):
    """
    检查单种方法的稳定度

    参数:
        history_list: 历史数据列表
        method: 'duima' 或 'sum_tail'
        periods: 回测期数，默认30期

    返回:
        (正确率, 是否稳定, 正确次数, 总次数)
    """
    check_func = check_duima_result if method == 'duima' else check_sum_tail_result

    test_data = history_list[:periods+1]
    total = 0
    correct_count = 0

    for i in range(len(test_data) - 1):
        last_num = test_data[i+1]['number']
        result_num = test_data[i]['number']

        is_correct, _, _ = check_func(result_num, last_num)
        if is_correct:
            correct_count += 1
        total += 1

    correct_rate = correct_count / total * 100 if total > 0 else 0
    is_stable = correct_rate >= 85

    return correct_rate, is_stable, correct_count, total


def check_stability_combined(history_list, periods=30):
    """
    检查组合方法的稳定度（两种方法都正确才算稳定）

    参数:
        history_list: 历史数据列表
        periods: 回测期数，默认30期

    返回:
        (正确率, 是否稳定, 正确次数, 总次数)
    """
    test_data = history_list[:periods+1]
    total = 0
    correct_count = 0

    for i in range(len(test_data) - 1):
        last_num = test_data[i+1]['number']
        result_num = test_data[i]['number']

        is_correct, _, _, _ = check_combined_result(result_num, last_num)
        if is_correct:
            correct_count += 1
        total += 1

    correct_rate = correct_count / total * 100 if total > 0 else 0
    is_stable = correct_rate >= 85

    return correct_rate, is_stable, correct_count, total


def main():
    """主函数：显示对码法与和值尾四六分解分析结果"""
    import json

    with open('c:/Users/zhao/WorkBuddy/Claw/data/all_history.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    data_pl3 = sorted([d for d in data if d['type'] == 'pl3'], key=lambda x: x['period'], reverse=True)
    data_3d = sorted([d for d in data if d['type'] == '3d'], key=lambda x: x['period'], reverse=True)

    print("=" * 60)
    print("对码法 & 和值尾四六分解")
    print("=" * 60)
    print("\n【规则】两边都有不同数字 = 正确，只有一边有 = 错误\n")

    for name, history in [('排列三', data_pl3), ('3D', data_3d)]:
        duima_result = analyze_duima_method(history)
        sum_tail_result = analyze_sum_tail_method(history)
        combined_result = analyze_combined_method(history)

        # 稳定度检查
        duima_rate, duima_stable, duima_correct, duima_total = check_stability_single(history, 'duima', 30)
        sum_tail_rate, sum_tail_stable, sum_tail_correct, sum_tail_total = check_stability_single(history, 'sum_tail', 30)
        combined_rate, combined_stable, combined_correct, combined_total = check_stability_combined(history, 30)

        print(f"{'='*50}")
        print(f"【{name}】上期奖号: {duima_result['last_number']}")
        print(f"{'='*50}")

        print(f"\n[对码法]")
        print(f"  对码组(6个): {duima_result['duima_group']}")
        print(f"  剩余组(4个): {duima_result['remaining_group']}")
        print(f"  分解结果: {duima_result['result']}")

        print(f"\n[和值尾四六分解]")
        print(f"  和值尾: {sum_tail_result['sum_tail']}")
        print(f"  4码组: {sum_tail_result['group4']}")
        print(f"  6码组: {sum_tail_result['group6']}")
        print(f"  分解结果: {sum_tail_result['result']}")

        print(f"\n[组合使用]")
        print(f"  对码组: {combined_result['duima_group']}")
        print(f"  4码组: {combined_result['group4']}")
        print(f"  交集(杀号): {combined_result['intersection']}")

        # 稳定度警告
        print(f"\n[稳定度检查 - 最近30期]")
        print(f"  对码法: {duima_rate:.1f}% ({duima_correct}/{duima_total})")
        if duima_stable:
            print(f"    -> 稳定，可放心使用")
        else:
            print(f"    -> [WARN] 近期不太稳定，谨慎使用")

        print(f"  和值尾四六分解: {sum_tail_rate:.1f}% ({sum_tail_correct}/{sum_tail_total})")
        if sum_tail_stable:
            print(f"    -> 稳定，可放心使用")
        else:
            print(f"    -> [WARN] 近期不太稳定，谨慎使用")

        print(f"  组合(两种都正确): {combined_rate:.1f}% ({combined_correct}/{combined_total})")
        if combined_stable:
            print(f"    -> 稳定，可放心使用")
        else:
            print(f"    -> [WARN] 近期不太稳定，谨慎使用")

        print()


if __name__ == '__main__':
    main()