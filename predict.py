import json
from collections import Counter

with open('c:/Users/zhao/WorkBuddy/Claw/data/all_history.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data_3d = sorted([d for d in data if d['type'] == '3d'], key=lambda x: x['period'], reverse=True)
data_pl3 = sorted([d for d in data if d['type'] == 'pl3'], key=lambda x: x['period'], reverse=True)

def get_num_frequency(history, count=30):
    """获取数字出现频率"""
    freq = {i: 0 for i in range(10)}
    for item in history[:count]:
        num = item['number']
        freq[int(num[0])] += 1
        freq[int(num[1])] += 1
        freq[int(num[2])] += 1
    return freq

def get_position_frequency(history, count=50):
    """获取位置频率"""
    pos1, pos2, pos3 = {i: 0 for i in range(10)}, {i: 0 for i in range(10)}, {i: 0 for i in range(10)}
    for item in history[:count]:
        num = item['number']
        pos1[int(num[0])] += 1
        pos2[int(num[1])] += 1
        pos3[int(num[2])] += 1
    return {'pos1': pos1, 'pos2': pos2, 'pos3': pos3}

def get_top_n(freq, n=5):
    """获取频率最高的N个数字"""
    return [int(k) for k, v in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]]

def predict_sum(history, count=50):
    """预测和值"""
    sums = {i: 0 for i in range(28)}
    for item in history[:count]:
        num = item['number']
        s = int(num[0]) + int(num[1]) + int(num[2])
        sums[s] += 1
    # 取频率最高的2个和值
    return [int(k) for k, v in sorted(sums.items(), key=lambda x: x[1], reverse=True)[:2]]

def analyze_334(history, count=30):
    """334断组分析"""
    groups = {
        'g1': {'nums': [0, 1, 2], 'count': 0},
        'g2': {'nums': [3, 4, 5], 'count': 0},
        'g3': {'nums': [6, 7, 8, 9], 'count': 0}
    }
    for item in history[:count]:
        num = item['number']
        nums = [int(n) for n in num]
        for n in nums:
            if n in groups['g1']['nums']: groups['g1']['count'] += 1
            if n in groups['g2']['nums']: groups['g2']['count'] += 1
            if n in groups['g3']['nums']: groups['g3']['count'] += 1
    return groups

def analyze_55(history, count=30):
    """55分解分析"""
    group_a, group_b = 0, 0
    for item in history[:count]:
        num = item['number']
        nums = [int(n) for n in num]
        if any(n <= 4 for n in nums): group_a += 1
        if any(n >= 5 for n in nums): group_b += 1
    return {'a': group_a, 'b': group_b}

def generate_bets(pos1, pos2, pos3, sums):
    """生成四注推荐"""
    bets = []
    used = set()

    # 方法: 直接组合位置TOP5
    for i in range(5):
        for j in range(5):
            for k in range(5):
                bet = f'{pos1[i]}{pos2[j]}{pos3[k]}'
                if bet not in used:
                    used.add(bet)
                    bets.append(bet)
                if len(bets) >= 4:
                    break
            if len(bets) >= 4:
                break
        if len(bets) >= 4:
            break

    return bets[:4]

def analyze(data, name):
    print(f'\n========== {name} ==========')
    print(f'最新期号: {data[0]["period"]} ({data[0]["date"]})')
    print(f'最新号码: {data[0]["number"]}')
    print()

    # 1. 金银胆 (30期)
    freq30 = get_num_frequency(data, 30)
    sorted_freq = sorted(freq30.items(), key=lambda x: x[1], reverse=True)
    gold = sorted_freq[0][0]
    silver = sorted_freq[1][0]
    print(f'金胆: {gold} ({sorted_freq[0][1]}次/30期)')
    print(f'银胆: {silver} ({sorted_freq[1][1]}次/30期)')

    # 2. 五码 (30期频率)
    top5 = get_top_n(freq30, 5)
    print(f'五码: {" ".join(map(str, top5))}')

    # 3. 位置频率 (50期)
    pos_freq = get_position_frequency(data, 50)
    pos1_top5 = get_top_n(pos_freq['pos1'], 5)
    pos2_top5 = get_top_n(pos_freq['pos2'], 5)
    pos3_top5 = get_top_n(pos_freq['pos3'], 5)
    print(f'百位TOP5: {" ".join(map(str, pos1_top5))}')
    print(f'十位TOP5: {" ".join(map(str, pos2_top5))}')
    print(f'个位TOP5: {" ".join(map(str, pos3_top5))}')

    # 4. 和值 (50期)
    sum_pred = predict_sum(data, 50)
    print(f'和值推荐: {sum_pred[0]}, {sum_pred[1]}')

    # 5. 四注
    bets = generate_bets(pos1_top5, pos2_top5, pos3_top5, sum_pred)
    print(f'四注: {" ".join(bets)}')

    # 6. 334断组 (30期)
    duan = analyze_334(data, 30)
    print(f'334断组: 012={duan["g1"]["count"]}次 345={duan["g2"]["count"]}次 6789={duan["g3"]["count"]}次')
    weak = min(duan.items(), key=lambda x: x[1]['count'])[0]
    print(f'较弱组: {weak}')

    # 7. 55分解 (30期)
    fj = analyze_55(data, 30)
    print(f'55分解: 0-4={fj["a"]}次 5-9={fj["b"]}次')

    return {
        'gold': gold,
        'silver': silver,
        'top5': top5,
        'bets': bets,
        'sums': sum_pred
    }

# 执行预测
print('=' * 50)
print('2026-04-03 预测结果 (与网页算法一致)')
print('=' * 50)

result_3d = analyze(data_3d, '3D')
result_pl3 = analyze(data_pl3, '排列三')
