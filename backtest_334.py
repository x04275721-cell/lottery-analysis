#!/usr/bin/env python3
"""
334断组回测 - 验证三种方法的准确率
"""

import json

# 对码表
DUIMA_PAIRS = {
    '0': '5', '5': '0',
    '1': '6', '6': '1',
    '2': '7', '7': '2',
    '3': '8', '8': '3',
    '4': '9', '9': '4'
}

# 和跨合尾查表334断组表
HEKUA_334_TABLE = {
    '0': ['019', '2378', '456'], '5': ['019', '2378', '456'],
    '1': ['012', '3489', '567'], '6': ['012', '3489', '567'],
    '2': ['123', '0459', '678'], '7': ['123', '0459', '678'],
    '3': ['234', '0156', '789'], '8': ['234', '0156', '789'],
    '4': ['345', '1267', '089'], '9': ['345', '1267', '089']
}


def make334_duima(last_num):
    """方法一：对码断组法"""
    duima_set = set()
    for d in last_num:
        duima_set.add(d)
        duima_set.add(DUIMA_PAIRS[d])
    merged = sorted(duima_set)

    if len(merged) == 4:
        g4 = ''.join(merged)
        remaining_set = set('0123456789')
        for d in merged:
            remaining_set.discard(d)
        remaining = sorted(remaining_set)
        g3a = ''.join(remaining[:3])
        g3b = ''.join(remaining[3:])
    else:
        remaining_set = set('0123456789')
        for d in merged:
            remaining_set.discard(d)
        remaining_from_other = sorted(remaining_set)
        g4 = ''.join(merged[:4])
        merged_remaining = merged[4:]
        combined = sorted(merged_remaining + remaining_from_other)
        g3a = ''.join(combined[:3])
        g3b = ''.join(combined[3:])
    return g4, g3a, g3b


def make334_hekua(last_num):
    """方法二：和跨合尾查表法"""
    s = sum(int(d) for d in last_num)
    nums = sorted(int(d) for d in last_num)
    kuadu = nums[2] - nums[0]
    tail = str((s + kuadu) % 10)
    groups = HEKUA_334_TABLE[tail]
    return groups[1], groups[0], groups[2]


def make334_linhao(last_num):
    """方法三：奖号邻号法"""
    nums = [int(d) for d in last_num]

    plus1 = sorted([(n + 1) % 10 for n in nums])
    minus1 = sorted([(n + 9) % 10 for n in nums])

    plus1_set = sorted(set(plus1))[:3]
    minus1_set = sorted(set(minus1))[:3]

    remaining_set = set(range(10)) - set(nums)
    remaining = sorted(remaining_set)

    g3a_plus = ''.join(map(str, plus1_set))
    g3b_plus = ''.join(map(str, remaining[:3]))
    g4_plus = ''.join(map(str, remaining[3:]))

    g3a_minus = ''.join(map(str, minus1_set))
    g3b_minus = ''.join(map(str, remaining[:3]))
    g4_minus = ''.join(map(str, remaining[3:]))

    # 简单返回方案A（+1）
    return g4_plus, g3a_plus, g3b_plus


def check334_correct(result_num, g4, g3a, g3b):
    """检查334断组是否正确（非1-1-1分布=正确）"""
    unique = set(result_num)
    in4 = sum(1 for d in unique if d in g4)
    in3a = sum(1 for d in unique if d in g3a)
    in3b = sum(1 for d in unique if d in g3b)

    # 1-1-1分布 = 失败
    if in4 == 1 and in3a == 1 and in3b == 1:
        return False
    return True


def backtest_334(data, periods=30):
    """回测334断组三种方法的准确率"""
    test_data = data[:periods + 1]

    results = {
        'duima': {'correct': 0, 'wrong': 0},
        'hekua': {'correct': 0, 'wrong': 0},
        'linhao': {'correct': 0, 'wrong': 0}
    }

    print(f"\n{'='*70}")
    print(f"  334断组回测 (最近{periods}期)")
    print(f"{'='*70}")
    print(f"\n{'期号':<10} {'上期':<8} {'开奖':<8} | {'对码法':<15} {'和跨法':<15} {'邻号法':<15}")
    print('-' * 85)

    for i in range(len(test_data) - 1):
        period = test_data[i]['period']
        last_num = test_data[i + 1]['number']
        result_num = test_data[i]['number']

        # 三种方法
        g4_d, g3a_d, g3b_d = make334_duima(last_num)
        g4_h, g3a_h, g3b_h = make334_hekua(last_num)
        g4_l, g3a_l, g3b_l = make334_linhao(last_num)

        # 检查
        ok_d = check334_correct(result_num, g4_d, g3a_d, g3b_d)
        ok_h = check334_correct(result_num, g4_h, g3a_h, g3b_h)
        ok_l = check334_correct(result_num, g4_l, g3a_l, g3b_l)

        if ok_d:
            results['duima']['correct'] += 1
        else:
            results['duima']['wrong'] += 1

        if ok_h:
            results['hekua']['correct'] += 1
        else:
            results['hekua']['wrong'] += 1

        if ok_l:
            results['linhao']['correct'] += 1
        else:
            results['linhao']['wrong'] += 1

        status_d = "[OK]" if ok_d else "[X]"
        status_h = "[OK]" if ok_h else "[X]"
        status_l = "[OK]" if ok_l else "[X]"

        print(f"{period:<10} {last_num:<8} {result_num:<8} | {g4_d}/{g3a_d}/{g3b_d} {status_d}  {g4_h}/{g3a_h}/{g3b_h} {status_h}  {g4_l}/{g3a_l}/{g3b_l} {status_l}")

    print('-' * 85)

    # 统计
    total = periods
    for method in ['duima', 'hekua', 'linhao']:
        correct = results[method]['correct']
        wrong = results[method]['wrong']
        rate = correct / total * 100 if total > 0 else 0
        method_name = {'duima': '对码断组法', 'hekua': '和跨查表法', 'linhao': '邻号法'}[method]
        print(f"\n{method_name}:")
        print(f"  正确: {correct}/{total} = {rate:.1f}%")
        print(f"  错误: {wrong}/{total} = {100-rate:.1f}%")

    return results


def backtest_multi_periods(data):
    """多期回测（30期、50期、100期）"""
    print(f"\n{'='*70}")
    print(f"  多期准确率统计")
    print(f"{'='*70}")
    print(f"\n{'期数':<8} {'对码法':<15} {'和跨法':<15} {'邻号法':<15}")
    print('-' * 60)

    for periods in [30, 50, 100]:
        if len(data) < periods + 1:
            continue

        test_data = data[:periods + 1]
        counts = {'duima': 0, 'hekua': 0, 'linhao': 0}

        for i in range(len(test_data) - 1):
            last_num = test_data[i + 1]['number']
            result_num = test_data[i]['number']

            g4_d, g3a_d, g3b_d = make334_duima(last_num)
            g4_h, g3a_h, g3b_h = make334_hekua(last_num)
            g4_l, g3a_l, g3b_l = make334_linhao(last_num)

            if check334_correct(result_num, g4_d, g3a_d, g3b_d):
                counts['duima'] += 1
            if check334_correct(result_num, g4_h, g3a_h, g3b_h):
                counts['hekua'] += 1
            if check334_correct(result_num, g4_l, g3a_l, g3b_l):
                counts['linhao'] += 1

        total = periods
        rate_d = counts['duima'] / total * 100
        rate_h = counts['hekua'] / total * 100
        rate_l = counts['linhao'] / total * 100

        print(f"{periods:<8} {rate_d:.1f}% ({counts['duima']}/{total})  {rate_h:.1f}% ({counts['hekua']}/{total})  {rate_l:.1f}% ({counts['linhao']}/{total})")


if __name__ == '__main__':
    # 读取数据
    with open('c:/Users/zhao/WorkBuddy/Claw/data/all_history.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 分离并排序
    data_3d = sorted([d for d in data if d['type'] == '3d'], key=lambda x: x['period'], reverse=True)
    data_pl3 = sorted([d for d in data if d['type'] == 'pl3'], key=lambda x: x['period'], reverse=True)

    print(f"\n数据概览:")
    print(f"3D: {len(data_3d)}条, 最新期号 {data_3d[0]['period']}")
    print(f"排列三: {len(data_pl3)}条, 最新期号 {data_pl3[0]['period']}")

    # 3D回测
    print(f"\n{'#'*70}")
    print(f"  3D 334断组回测")
    print(f"{'#'*70}")
    backtest_334(data_3d, 30)
    backtest_multi_periods(data_3d)

    # 排列三回测
    print(f"\n{'#'*70}")
    print(f"  排列三 334断组回测")
    print(f"{'#'*70}")
    backtest_334(data_pl3, 30)
    backtest_multi_periods(data_pl3)