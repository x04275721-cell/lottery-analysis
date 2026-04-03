# -*- coding: utf-8 -*-
"""
彩票预测系统 V6.0
体彩排列三 / 福彩3D
包含五码、四注号、金银胆、和值预测
"""

import json
import os
import sys
from datetime import datetime
from collections import Counter

# 确保UTF-8输出
sys.stdout.reconfigure(encoding='utf-8')

# 尝试导入预测模块
try:
    from hezx_sum import predict_sum
except ImportError:
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


def analyze_ji_bai(history_list):
    """奇偶比分析"""
    if not history_list:
        return {'奇数': 5, '偶数': 5}

    ji_count = 0
    ou_count = 0

    for item in history_list[:30]:
        for num in [item['num1'], item['num2'], item['num3']]:
            if int(num) % 2 == 1:
                ji_count += 1
            else:
                ou_count += 1

    return {'奇数': ji_count, '偶数': ou_count}


def analyze_da_xiao(history_list):
    """大小比分析"""
    if not history_list:
        return {'大数': 5, '小数': 5}

    da_count = 0
    xiao_count = 0

    for item in history_list[:30]:
        for num in [item['num1'], item['num2'], item['num3']]:
            if int(num) >= 5:
                da_count += 1
            else:
                xiao_count += 1

    return {'大数': da_count, '小数': xiao_count}


def analyze_zhi_he(history_list):
    """质合比分析"""
    if not history_list:
        return {'质数': 5, '合数': 5}

    zhi_count = 0
    he_count = 0

    for item in history_list[:30]:
        for num in [item['num1'], item['num2'], item['num3']]:
            if int(num) in [1, 2, 3, 5, 7]:
                zhi_count += 1
            else:
                he_count += 1

    return {'质数': zhi_count, '合数': he_count}


def analyze_334_duan(history_list):
    """
    334断组分析
    将0-9分成3、3、4三组，分析近期哪组容易断

    常见分组：012 / 345 / 6789
    """
    if not history_list:
        return {'组1(012)': 0, '组2(345)': 0, '组3(6789)': 0, '预测断组': '组1'}

    group1 = {'0', '1', '2'}
    group2 = {'3', '4', '5'}
    group3 = {'6', '7', '8', '9'}

    g1_count, g2_count, g3_count = 0, 0, 0

    for item in history_list[:30]:
        nums = {item['num1'], item['num2'], item['num3']}
        if group1 & nums:
            g1_count += 1
        if group2 & nums:
            g2_count += 1
        if group3 & nums:
            g3_count += 1

    total = len(history_list[:30]) if len(history_list) >= 30 else len(history_list)
    counts = {'组1(012)': g1_count, '组2(345)': g2_count, '组3(6789)': g3_count}
    predict_dan = min(counts, key=counts.get)

    return {
        '组1(012)': g1_count,
        '组2(345)': g2_count,
        '组3(6789)': g3_count,
        '预测断组': predict_dan
    }


def analyze_55_fenjie(history_list):
    """
    55分解分析
    将0-9分成5、5两组：01234 / 56789
    """
    if not history_list:
        return {'前组(0-4)': 0, '后组(5-9)': 0, '预测偏向': '前组'}

    group_a = {'0', '1', '2', '3', '4'}
    group_b = {'5', '6', '7', '8', '9'}

    a_count, b_count = 0, 0

    for item in history_list[:30]:
        nums = {item['num1'], item['num2'], item['num3']}
        if group_a & nums:
            a_count += 1
        if group_b & nums:
            b_count += 1

    total = len(history_list[:30]) if len(history_list) >= 30 else len(history_list)
    predict = '前组(0-4)' if a_count > b_count else '后组(5-9)'

    return {
        '前组(0-4)': a_count,
        '后组(5-9)': b_count,
        '预测偏向': predict
    }


def analyze_wuxiao(history_list, top_n=5):
    """五码推荐"""
    if len(history_list) < 10:
        return {'位1': ['0', '1', '2', '3', '4'], '位2': ['0', '1', '2', '3', '4'], '位3': ['0', '1', '2', '3', '4']}

    position_stats = {'位1': {}, '位2': {}, '位3': {}}

    for item in history_list[:50]:
        for i, pos in enumerate(['位1', '位2', '位3']):
            num = item[f'num{i+1}']
            position_stats[pos][num] = position_stats[pos].get(num, 0) + 1

    result = {}
    for pos in ['位1', '位2', '位3']:
        sorted_nums = sorted(position_stats[pos].items(), key=lambda x: -x[1])
        result[pos] = [n for n, _ in sorted_nums[:top_n]]

    return result


def analyze_dan(history_list):
    """金银胆分析"""
    if len(history_list) < 5:
        return {'金胆': '0', '银胆': '1'}

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
    """四注号推荐"""
    if len(history_list) < 20:
        return ['012', '345', '678', '901']

    wuxiao = analyze_wuxiao(history_list)
    candidates = []
    for n1 in wuxiao.get('位1', ['0', '1', '2', '3', '4'])[:3]:
        for n2 in wuxiao.get('位2', ['0', '1', '2', '3', '4'])[:3]:
            for n3 in wuxiao.get('位3', ['0', '1', '2', '3', '4'])[:3]:
                candidates.append(n1 + n2 + n3)

    return candidates[:4] if candidates else ['012', '345', '678', '901']


def get_latest_result(history_list):
    """获取最新一期开奖结果"""
    if not history_list:
        return {'期号': '暂无数据', '号码': '---'}
    latest = history_list[0]
    return {
        '期号': latest.get('period', '未知'),
        '号码': f"{latest['num1']}{latest['num2']}{latest['num3']}"
    }


def analyze(name, history_list):
    """完整分析"""
    if not history_list:
        return {
            'name': name,
            'latest': {'期号': '暂无数据', '号码': '---'},
            'wuxiao': {'位1': ['-'], '位2': ['-'], '位3': ['-']},
            'dan': {'金胆': '-', '银胆': '-'},
            'sizhu': ['----', '----', '----', '----'],
            'sums': [0, 1],
            'ji_bai': {'奇数': 0, '偶数': 0},
            'da_xiao': {'大数': 0, '小数': 0},
            'zhi_he': {'质数': 0, '合数': 0},
            '334_duan': {'组1(012)': 0, '组2(345)': 0, '组3(6789)': 0, '预测断组': '-'},
            '55_fenjie': {'前组(0-4)': 0, '后组(5-9)': 0, '预测偏向': '-'}
        }

    import pandas as pd
    df = pd.DataFrame(history_list)

    ji_bai = analyze_ji_bai(history_list)
    da_xiao = analyze_da_xiao(history_list)
    zhi_he = analyze_zhi_he(history_list)
    wuxiao = analyze_wuxiao(history_list)
    dan = analyze_dan(history_list)
    sizhu = analyze_si_zhu(history_list)
    sums, _ = predict_sum(df)
    duan_334 = analyze_334_duan(history_list)
    fenjie_55 = analyze_55_fenjie(history_list)

    return {
        'name': name,
        'latest': get_latest_result(history_list),
        'wuxiao': wuxiao,
        'dan': dan,
        'sizhu': sizhu,
        'sums': sums,
        'ji_bai': ji_bai,
        'da_xiao': da_xiao,
        'zhi_he': zhi_he,
        '334_duan': duan_334,
        '55_fenjie': fenjie_55
    }


def main():
    """主函数"""
    pl3_history = load_history('data/pl3_history.json')
    d3_history = load_history('data/3d_history.json')

    pl3_result = analyze('排列三', pl3_history)
    d3_result = analyze('3D', d3_history)

    results = {'pl3': pl3_result, '3d': d3_result}
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return results


if __name__ == '__main__':
    main()
