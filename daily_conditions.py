# -*- coding: utf-8 -*-
"""
每日彩票数据生成
根据最新历史数据，生成当日推荐条件
包含：五码、四注号、金银胆、和值预测
"""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import Counter

# 尝试导入预测模块
try:
    from hezx_sum import predict_sum
except ImportError:
    # 如果找不到模块，定义简化版本
    def predict_sum(df, count=2):
        sums = [int(row['num1']) + int(row['num2']) + int(row['num3'])
                for _, row in df.head(50).iterrows()]
        sum_count = Counter(sums)
        return [s for s, _ in sum_count.most_common(count)], sum_count


def load_history(filepath):
    """加载历史数据"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


def analyze_wuxiao(history_list, top_n=5):
    """
    分析五码推荐 - 基于位置频率统计

    返回:
        dict: {'位1': [数字列表], '位2': [...], ...}
    """
    if len(history_list) < 10:
        return {'位1': ['0', '1', '2', '3', '4'], '位2': ['0', '1', '2', '3', '4'], '位3': ['0', '1', '2', '3', '4']}

    # 统计每个位置各数字出现频率
    position_stats = {'位1': {}, '位2': {}, '位3': {}}

    for item in history_list[:50]:  # 只看近50期
        for i, pos in enumerate(['位1', '位2', '位3']):
            num = item[f'num{i+1}']
            position_stats[pos][num] = position_stats[pos].get(num, 0) + 1

    # 取每个位置频率最高的数字
    result = {}
    for pos in ['位1', '位2', '位3']:
        sorted_nums = sorted(position_stats[pos].items(), key=lambda x: -x[1])
        result[pos] = [n for n, _ in sorted_nums[:top_n]]

    return result


def analyze_dan(history_list):
    """
    分析金胆银胆 - 基于冷热分析

    返回:
        dict: {'金胆': 'X', '银胆': 'X'}
    """
    if len(history_list) < 5:
        return {'金胆': '0', '银胆': '1'}

    # 统计所有数字出现频率
    all_nums = []
    for item in history_list[:30]:
        all_nums.extend([item['num1'], item['num2'], item['num3']])

    num_count = Counter(all_nums)
    sorted_nums = [n for n, _ in num_count.most_common(10)]

    return {
        '金胆': sorted_nums[0] if len(sorted_nums) > 0 else '0',
        '银胆': sorted_nums[1] if len(sorted_nums) > 1 else '1'
    }


def analyze_si_zhu(history_list):
    """
    分析四注号码 - 基于多条件筛选

    返回:
        list: ['XXX', 'XXX', 'XXX', 'XXX']
    """
    if len(history_list) < 20:
        return ['012', '345', '678', '901']

    # 获取五码
    wuxiao = analyze_wuxiao(history_list)

    # 生成候选号码（使用五码组合）
    candidates = []
    for n1 in wuxiao.get('位1', ['0', '1', '2', '3', '4'])[:3]:
        for n2 in wuxiao.get('位2', ['0', '1', '2', '3', '4'])[:3]:
            for n3 in wuxiao.get('位3', ['0', '1', '2', '3', '4'])[:3]:
                candidates.append(n1 + n2 + n3)

    # 取4个候选（简化处理）
    return candidates[:4] if candidates else ['012', '345', '678', '901']


def generate_daily_conditions(pl3_history, d3_history):
    """
    生成每日推荐数据

    返回:
        dict: 包含体彩排列三和福彩3D的推荐数据
    """
    def process_single(history_list, name):
        if not history_list:
            return {
                '五码': {'位1': ['0', '1', '2', '3', '4'], '位2': ['0', '1', '2', '3', '4'], '位3': ['0', '1', '2', '3', '4']},
                '金胆': '0', '银胆': '1',
                '四注号': ['012', '345', '678', '901'],
                '和值': [10, 11],
                '更新': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        # 构建DataFrame用于分析
        import pandas as pd
        df = pd.DataFrame(history_list)

        # 五码分析
        wuxiao = analyze_wuxiao(history_list)

        # 金银胆
        dan = analyze_dan(history_list)

        # 四注号
        sizhu = analyze_si_zhu(history_list)

        # 和值预测
        sums, _ = predict_sum(df)

        return {
            '五码': wuxiao,
            '金胆': dan['金胆'],
            '银胆': dan['银胆'],
            '四注号': sizhu,
            '和值': sums,
            '更新': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    return {
        'pl3': process_single(pl3_history, '排列三'),
        '3d': process_single(d3_history, '3D')
    }


def save_daily_conditions(conditions):
    """保存每日数据到JSON文件"""
    os.makedirs('data', exist_ok=True)

    # 保存主文件
    with open('data/daily_conditions.json', 'w', encoding='utf-8') as f:
        json.dump(conditions, f, ensure_ascii=False, indent=2)

    # 保存带日期的备份
    date_str = datetime.now().strftime('%Y%m%d')
    backup_path = f'data/daily_conditions_{date_str}.json'
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(conditions, f, ensure_ascii=False, indent=2)


def main():
    """主函数 - 生成当日推荐"""
    print("正在加载历史数据...")

    pl3_history = load_history('data/pl3_history.json')
    d3_history = load_history('data/3d_history.json')

    print(f"排列三: {len(pl3_history)} 期数据")
    print(f"3D: {len(d3_history)} 期数据")

    if not pl3_history and not d3_history:
        print("没有历史数据，请先运行 fetch_history.py 获取数据")
        return

    print("正在生成推荐条件...")
    conditions = generate_daily_conditions(pl3_history, d3_history)

    save_daily_conditions(conditions)
    print("每日推荐数据已生成!")

    # 输出到控制台（供GitHub Actions使用）
    print("\n=== 当日推荐 ===")
    print(json.dumps(conditions, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
