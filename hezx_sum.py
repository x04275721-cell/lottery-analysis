# -*- coding: utf-8 -*-
"""
和值预测模块
统计近期和值出现频率，预测最可能出现的和值
"""

import pandas as pd
from collections import Counter


def predict_sum(df, count=2):
    """
    和值预测 - 统计近期和值出现频率

    参数:
        df: 包含num1, num2, num3列的历史DataFrame
        count: 返回前N个最可能的和值，默认2个

    返回:
        top_sums: 出现频率最高的和值列表
        sum_count: 所有和值的计数器
    """
    if len(df) < 10:
        return [10, 11], Counter()  # 默认和值

    sums = []
    for _, row in df.head(50).iterrows():
        s = int(row['num1']) + int(row['num2']) + int(row['num3'])
        sums.append(s)

    sum_count = Counter(sums)
    top_sums = [s for s, _ in sum_count.most_common(count)]

    return top_sums, sum_count


def get_sum_distribution(df):
    """
    获取和值分布统计

    返回:
        dict: {和值: 出现次数}
    """
    sums = [int(row['num1']) + int(row['num2']) + int(row['num3'])
            for _, row in df.iterrows()]
    return dict(Counter(sums))


def is_sum_hit(actual_sum, predicted_sums):
    """
    判断和值是否命中

    参数:
        actual_sum: 实际和值
        predicted_sums: 预测的和值列表

    返回:
        bool: 是否命中
    """
    return actual_sum in predicted_sums
