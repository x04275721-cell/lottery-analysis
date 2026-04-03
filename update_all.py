# -*- coding: utf-8 -*-
"""
每日更新总控脚本
自动获取最新数据并更新每日推荐
用于GitHub Actions定时任务
"""

import os
import sys
import json
from datetime import datetime

# 确保UTF-8输出
sys.stdout.reconfigure(encoding='utf-8')


def main():
    print("=" * 50)
    print("彩票预测系统 - 每日更新")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 创建data目录
    os.makedirs('data', exist_ok=True)

    # 1. 获取历史数据
    print("\n[1/3] 获取最新历史数据...")
    try:
        from fetch_history import fetch_and_save_all
        fetch_and_save_all(500)
        print("历史数据获取完成")
    except Exception as e:
        print(f"获取历史数据失败: {e}")
        # 继续尝试使用现有数据

    # 2. 生成每日推荐
    print("\n[2/3] 生成每日推荐条件...")
    try:
        from daily_conditions import main as generate_conditions
        generate_conditions()
        print("每日推荐生成完成")
    except Exception as e:
        print(f"生成推荐失败: {e}")

    # 3. 保存更新记录
    print("\n[3/3] 保存更新记录...")
    update_log = {
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'success'
    }

    with open('data/update_log.json', 'w', encoding='utf-8') as f:
        json.dump(update_log, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 50)
    print("每日更新完成!")
    print("=" * 50)


if __name__ == '__main__':
    main()
