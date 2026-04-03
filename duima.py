# -*- coding: utf-8 -*-
"""
对码法预测
利用"差5"对码：0-5, 1-6, 2-7, 3-8, 4-9

================================================================================
分解式规则
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

【分解式正确判断规则】
    核心原则：两边都要有不同数字

    统计开奖号中不同数字在对码组和剩余组的分布：
    - 1+2（组三跨两组）：正确
    - 2+1（组三跨两组）：正确
    - 1+1（组三，对码组和剩余组各一个不同数字）：正确
    - 3+0（豹子或三同号，全部在对码组）：错误
    - 0+3（豹子或三同号，全部在剩余组）：错误
    - 2+0（组三，同组两个不同数字）：错误
    - 0+2（组三，同组两个不同数字）：错误

    简记：两边都有不同数字 = 正确，只有一边有 = 错误

【分布说明】
    - 1+2：开奖号有3个不同数字，1个在对的组，2个在剩余组
    - 2+1：开奖号有3个不同数字，2个在对的组，1个在剩余组
    - 1+1：开奖号只有2个不同数字（组三），各分布在一组
    - 3+0：开奖号3个不同数字全在对码组（豹子、组三全对码）
    - 0+3：开奖号3个不同数字全在剩余组（豹子、组三全剩余）
    - 2+0：开奖号只有2个不同数字，但都在对码组
    - 0+2：开奖号只有2个不同数字，但都在剩余组

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


def get_duima_pairs():
    """获取对码对"""
    return DUIMA_PAIRS.copy()


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
    检查分解式预判是否正确

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


def main():
    """主函数：显示对码分析结果"""
    import json

    with open('data/all_history.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    data_pl3 = sorted([d for d in data if d['type'] == 'pl3'], key=lambda x: x['period'], reverse=True)
    data_3d = sorted([d for d in data if d['type'] == '3d'], key=lambda x: x['period'], reverse=True)

    print("=" * 60)
    print("对码法分析")
    print("=" * 60)
    print("\n【规则】两边都有不同数字 = 正确，只有一边有 = 错误\n")

    for name, history in [('排列三', data_pl3), ('3D', data_3d)]:
        result = analyze_duima_method(history)
        print(f"【{name}】")
        print(f"  上期奖号: {result['last_number']}")
        print(f"  对码组(6个): {result['duima_group']}")
        print(f"  剩余组(4个): {result['remaining_group']}")
        print(f"  分解结果: {result['result']}")
        print()


if __name__ == '__main__':
    main()