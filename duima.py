# -*- coding: utf-8 -*-
"""
彩票分解式预测
包含两种方法：对码法、和值尾四六分解

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


def main():
    """主函数：显示对码法与和值尾四六分解分析结果"""
    import json

    with open('data/all_history.json', 'r', encoding='utf-8') as f:
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
        print()


if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()