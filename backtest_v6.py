# -*- coding: utf-8 -*-
"""
回测验证脚本
测试排列三和3D的预测命中率
使用滚动窗口：每次用前N期数据预测下一期
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime

# 确保UTF-8输出
sys.stdout.reconfigure(encoding='utf-8')


def load_history(filepath):
    """加载历史数据"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


def predict_sum_simple(history_list, count=2):
    """简化和值预测"""
    if len(history_list) < 10:
        return [10, 11]

    sums = [int(item['num1']) + int(item['num2']) + int(item['num3'])
            for item in history_list[-50:]]
    sum_count = Counter(sums)
    return [s for s, _ in sum_count.most_common(count)]


def predict_wuxiao(history_list, top_n=5):
    """预测五码"""
    if len(history_list) < 10:
        return {'位1': ['0', '1', '2', '3', '4'], '位2': ['0', '1', '2', '3', '4'], '位3': ['0', '1', '2', '3', '4']}

    position_stats = {'位1': {}, '位2': {}, '位3': {}}

    for item in history_list[-50:]:
        for i, pos in enumerate(['位1', '位2', '位3']):
            num = item[f'num{i+1}']
            position_stats[pos][num] = position_stats[pos].get(num, 0) + 1

    result = {}
    for pos in ['位1', '位2', '位3']:
        sorted_nums = sorted(position_stats[pos].items(), key=lambda x: -x[1])
        result[pos] = [n for n, _ in sorted_nums[:top_n]]

    return result


def predict_dan(history_list):
    """预测金银胆"""
    if len(history_list) < 5:
        return {'金胆': '0', '银胆': '1'}

    all_nums = []
    for item in history_list[-30:]:
        all_nums.extend([item['num1'], item['num2'], item['num3']])

    num_count = Counter(all_nums)
    sorted_nums = [n for n, _ in num_count.most_common(10)]

    return {
        '金胆': sorted_nums[0] if len(sorted_nums) > 0 else '0',
        '银胆': sorted_nums[1] if len(sorted_nums) > 1 else '1'
    }


def predict_sizhu(history_list):
    """预测四注号"""
    if len(history_list) < 20:
        return ['012', '345', '678', '901']

    wuxiao = predict_wuxiao(history_list)
    candidates = []
    for n1 in wuxiao.get('位1', ['0', '1', '2', '3', '4'])[:3]:
        for n2 in wuxiao.get('位2', ['0', '1', '2', '3', '4'])[:3]:
            for n3 in wuxiao.get('位3', ['0', '1', '2', '3', '4'])[:3]:
                candidates.append(n1 + n2 + n3)

    return candidates[:4] if candidates else ['012', '345', '678', '901']


def check_hit(actual, predicted):
    """检查是否命中"""
    return str(actual) in [str(p) for p in predicted]


def backtest_single(history_list, start_idx, end_idx):
    """
    单次回测

    返回:
        dict: 各指标命中情况
    """
    # 用[start_idx:end_idx]的数据预测
    past = history_list[start_idx:end_idx]
    if len(past) < 10:
        return None

    actual = history_list[end_idx]

    # 各指标预测
    wuxiao_pred = predict_wuxiao(past)
    dan_pred = predict_dan(past)
    sizhu_pred = predict_sizhu(past)
    sum_pred = predict_sum_simple(past)

    # 检查命中
    result = {
        '五码': {
            '位1': actual['num1'] in wuxiao_pred.get('位1', []),
            '位2': actual['num2'] in wuxiao_pred.get('位2', []),
            '位3': actual['num3'] in wuxiao_pred.get('位3', []),
        },
        '金胆': actual['num1'] == dan_pred['金胆'] or actual['num2'] == dan_pred['金胆'] or actual['num3'] == dan_pred['金胆'],
        '银胆': actual['num1'] == dan_pred['银胆'] or actual['num2'] == dan_pred['银胆'] or actual['num3'] == dan_pred['银胆'],
        '四注号': actual['num1'] + actual['num2'] + actual['num3'] in sizhu_pred,
        '和值': int(actual['num1']) + int(actual['num2']) + int(actual['num3']) in sum_pred
    }

    # 综合命中
    result['至少中1个'] = any(result['五码'].values()) or result['金胆'] or result['银胆'] or result['四注号'] or result['和值']
    result['五码全中'] = all(result['五码'].values())

    return result


def run_backtest(history_list, name, min_history=50, test_count=1000):
    """
    运行完整回测

    参数:
        history_list: 历史数据列表
        name: 数据名称（用于输出）
        min_history: 最少需要的历史期数
        test_count: 测试次数
    """
    if len(history_list) < min_history + test_count:
        print(f"{name}: 数据不足，需要 {min_history + test_count} 期，实际 {len(history_list)} 期")
        return None

    total = 0
    stats = {
        '五码_位1': 0, '五码_位2': 0, '五码_位3': 0, '五码全中': 0,
        '金胆': 0, '银胆': 0,
        '四注号': 0, '和值': 0,
        '至少中1个': 0
    }

    streak_current = 0
    streak_best = 0
    streak_count = 0
    max_streak = {'hit': 0, 'miss': 0}

    for i in range(test_count):
        start_idx = len(history_list) - test_count - min_history + i
        end_idx = len(history_list) - test_count + i

        result = backtest_single(history_list, start_idx, end_idx)
        if result is None:
            continue

        total += 1

        # 统计各指标
        for key in stats:
            if key in result and result[key]:
                stats[key] += 1

        # 连中连挂统计
        if result['至少中1个']:
            streak_count += 1
            if streak_count > max_streak['hit']:
                max_streak['hit'] = streak_count
        else:
            if streak_count > 0:
                streak_current = streak_count
                if streak_current > max_streak['miss']:
                    max_streak['miss'] = streak_current
            streak_count = 0

    # 最后处理
    if streak_count > max_streak['hit']:
        max_streak['hit'] = streak_count
    if streak_count > max_streak['miss']:
        max_streak['miss'] = streak_count

    # 计算命中率
    print(f"\n{'='*50}")
    print(f"{name} 回测结果 (共 {total} 期)")
    print(f"{'='*50}")
    print(f"五码命中率:")
    print(f"  - 位1: {stats['五码_位1']}/{total} = {stats['五码_位1']/total*100:.2f}%")
    print(f"  - 位2: {stats['五码_位2']}/{total} = {stats['五码_位2']/total*100:.2f}%")
    print(f"  - 位3: {stats['五码_位3']}/{total} = {stats['五码_位3']/total*100:.2f}%")
    print(f"  - 三位全中: {stats['五码全中']}/{total} = {stats['五码全中']/total*100:.2f}%")
    print(f"金胆: {stats['金胆']}/{total} = {stats['金胆']/total*100:.2f}%")
    print(f"银胆: {stats['银胆']}/{total} = {stats['银胆']/total*100:.2f}%")
    print(f"四注号: {stats['四注号']}/{total} = {stats['四注号']/total*100:.2f}%")
    print(f"和值: {stats['和值']}/{total} = {stats['和值']/total*100:.2f}%")
    print(f"至少中1个: {stats['至少中1个']}/{total} = {stats['至少中1个']/total*100:.2f}%")
    print(f"最大连中: {max_streak['hit']} 期")
    print(f"最大连挂: {max_streak['miss']} 期")

    return {
        'total': total,
        'stats': {k: f"{v}/{total} = {v/total*100:.2f}%" for k, v in stats.items()},
        'max_streak': max_streak
    }


def main():
    """主函数"""
    print("=" * 60)
    print("彩票预测回测系统")
    print("=" * 60)

    # 加载数据
    pl3_history = load_history('data/pl3_history.json')
    d3_history = load_history('data/3d_history.json')

    print(f"\n数据加载:")
    print(f"  排列三: {len(pl3_history)} 期")
    print(f"  3D: {len(d3_history)} 期")

    results = {}

    # 回测排列三
    if pl3_history:
        results['pl3'] = run_backtest(pl3_history, '体彩排列三', test_count=1000)

    # 回测3D
    if d3_history:
        results['3d'] = run_backtest(d3_history, '福彩3D', test_count=1000)

    # 汇总
    print(f"\n{'='*60}")
    print("汇总对比")
    print(f"{'='*60}")

    if 'pl3' in results and '3d' in results:
        print(f"\n{'指标':<15} {'排列三':<15} {'3D':<15}")
        print("-" * 45)
        for key in ['五码_位1', '金胆', '和值', '至少中1个']:
            pl3_rate = results['pl3']['stats'].get(key, 'N/A')
            d3_rate = results['3d']['stats'].get(key, 'N/A')
            print(f"{key:<15} {pl3_rate:<15} {d3_rate:<15}")

    print("\n回测完成!")


if __name__ == '__main__':
    main()
