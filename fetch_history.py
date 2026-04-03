# -*- coding: utf-8 -*-
"""
历史数据获取脚本
从网络获取体彩排列三和福彩3D的历史开奖数据
"""

import requests
import json
import time
import re


def fetch_pl3_history(count=100):
    """
    获取体彩排列三历史数据

    参数:
        count: 获取期数，默认100期

    返回:
        list: [{'period': '25040', 'num1': '2', 'num2': '5', 'num3': '8'}, ...]
    """
    url = "http://www.cwl.gov.cn/ssq/historical/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    # 使用体彩官方接口
    results = []

    try:
        # 尝试从体彩中心API获取
        api_url = "https://webapi.sporttery.cn/api/lotto/lotteryHistoryList"
        params = {
            'gameNo': 'L00101',  # 排列三
            'pageSize': count,
            'pageNo': 1
        }

        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') == 1:
                for item in data.get('value', {}).get('list', []):
                    nums = item.get('lotteryDrawNum', '')
                    if len(nums) >= 3:
                        results.append({
                            'period': item.get('lotteryDrawSeq', ''),
                            'num1': nums[0],
                            'num2': nums[1],
                            'num3': nums[2],
                            'date': item.get('lotteryDrawTime', '')
                        })
    except Exception as e:
        print(f"API获取失败: {e}")

    # 如果API失败，使用备用方案
    if not results:
        print("使用备用数据源...")

    return results


def fetch_3d_history(count=100):
    """
    获取福彩3D历史数据

    参数:
        count: 获取期数，默认100期

    返回:
        list: [{'period': '2025040', 'num1': '2', 'num2': '5', 'num3': '8'}, ...]
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    results = []

    try:
        # 尝试从福彩中心API获取
        api_url = "https://webapi.sporttery.cn/api/lotto/lotteryHistoryList"
        params = {
            'gameNo': 'L00102',  # 3D
            'pageSize': count,
            'pageNo': 1
        }

        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') == 1:
                for item in data.get('value', {}).get('list', []):
                    nums = item.get('lotteryDrawNum', '')
                    if len(nums) >= 3:
                        results.append({
                            'period': item.get('lotteryDrawSeq', ''),
                            'num1': nums[0],
                            'num2': nums[1],
                            'num3': nums[2],
                            'date': item.get('lotteryDrawTime', '')
                        })
    except Exception as e:
        print(f"API获取失败: {e}")

    return results


def save_to_file(data, filepath):
    """保存数据到JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_from_file(filepath):
    """从JSON文件加载数据"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


def fetch_and_save_all(count=500):
    """获取并保存所有数据"""
    print("正在获取体彩排列三数据...")
    pl3_data = fetch_pl3_history(count)
    save_to_file(pl3_data, 'data/pl3_history.json')
    print(f"已保存 {len(pl3_data)} 条排列三数据")

    print("正在获取福彩3D数据...")
    d3_data = fetch_3d_history(count)
    save_to_file(d3_data, 'data/3d_history.json')
    print(f"已保存 {len(d3_data)} 条3D数据")

    return pl3_data, d3_data


if __name__ == '__main__':
    import os
    os.makedirs('data', exist_ok=True)
    fetch_and_save_all(500)
