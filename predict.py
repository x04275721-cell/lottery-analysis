import json
from collections import Counter

with open('c:/Users/zhao/WorkBuddy/Claw/data/all_history.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data_3d = sorted([d for d in data if d['type'] == '3d'], key=lambda x: x['period'], reverse=True)
data_pl3 = sorted([d for d in data if d['type'] == 'pl3'], key=lambda x: x['period'], reverse=True)

def analyze(data, name, latest_period):
    print(f'\n========== {name} 预测分析 ==========')
    print(f'最新期号: {latest_period} ({data[0]["date"]})')
    print(f'最新号码: {data[0]["number"]}')
    print()

    # 最近100期分析
    recent = data[:100]
    all_nums = ''.join([d['number'] for d in recent])

    # 频率统计
    freq = Counter(all_nums)
    print('--- 近100期频率统计 ---')
    for num in sorted(freq.keys()):
        print(f'  {num}: {freq[num]}次', end='  ')
    print()

    # 金胆(频率最高)
    sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    gold_num = sorted_freq[0][0]
    silver_num = sorted_freq[1][0]
    print(f'\n金胆: {gold_num} ({sorted_freq[0][1]}次)')
    print(f'银胆: {silver_num} ({sorted_freq[1][1]}次)')

    # 位置频率分析
    print('\n--- 位置频率 (百/十/个) ---')
    pos1 = Counter([d['number'][0] for d in recent])
    pos2 = Counter([d['number'][1] for d in recent])
    pos3 = Counter([d['number'][2] for d in recent])

    for pos, name_p in [(pos1, '百'), (pos2, '十'), (pos3, '个')]:
        top3 = sorted(pos.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f'{name_p}位: {" ".join([n+"("+str(c)+"次)" for n,c in top3])}')

    # 和值统计
    sums = [sum(map(int, list(d['number']))) for d in recent]
    sum_freq = Counter(sums)
    top_sums = sorted(sum_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f'\n和值TOP5: {" ".join([str(s)+"("+str(c)+"次)" for s,c in top_sums])}')

    # 奇偶比例
    ji_ou = [('奇' if int(n)%2==1 else '偶') for n in list(d['number'] for d in recent[:20])]
    jo_cnt = Counter(ji_ou)
    print(f'近20期奇偶: 奇{jo_cnt["奇"]} 偶{jo_cnt["偶"]}')

    # 334断组分析
    g1 = [n for n in '012']
    g2 = [n for n in '345']
    g3 = [n for n in '6789']

    def get_group(n):
        if n in g1: return 1
        if n in g2: return 2
        return 3

    recent_10 = data[:10]
    groups_count = [0, 0, 0]
    for d in recent_10:
        groups = set([get_group(n) for n in d['number']])
        for g in groups:
            groups_count[g-1] += 1

    print(f'\n334断组近10期: 012组{groups_count[0]}次 345组{groups_count[1]}次 6789组{groups_count[2]}次')
    weak_group = groups_count.index(min(groups_count)) + 1
    print(f'较弱组: 第{weak_group}组 ({["012","345","6789"][weak_group-1]})')

    # 55分解
    group_a = sum(1 for n in all_nums if n in '01234')
    group_b = sum(1 for n in all_nums if n in '56789')
    print(f'\n55分解: 0-4组={group_a}次 5-9组={group_b}次')
    if group_a > group_b:
        print('偏向: 小数组(0-4)')
    else:
        print('偏向: 大数组(5-9)')

    # 遗漏值
    print('\n--- 遗漏值追踪 ---')
    last_appear = {}
    for i, d in enumerate(data):
        for n in d['number']:
            if n not in last_appear:
                last_appear[n] = i
    miss = {n: last_appear.get(n, 0) for n in '0123456789'}
    hot = [n for n, v in miss.items() if v < 5]
    cold = [n for n, v in miss.items() if v > 15]
    print(f'过热(遗漏<5): {" ".join(hot)}')
    print(f'过冷(遗漏>15): {" ".join(cold)}')

    # 生成推荐
    print('\n========== 推荐号码 ==========')
    top5_freq = [n for n, c in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]]
    print(f'五码推荐: {" ".join(top5_freq)}')

    # 生成4注
    import random
    random.seed(42)
    candidates = top5_freq + [gold_num, silver_num]
    candidates = list(set(candidates))

    # 基于频率的推荐组合
    recommendations = []
    for _ in range(4):
        nums = random.sample(candidates, 3)
        recommendations.append(''.join(nums))

    print(f'四注推荐: {" ".join(recommendations)}')

    return {
        'gold': gold_num,
        'silver': silver_num,
        'top5': top5_freq,
        'sums': [s for s, c in top_sums[:2]]
    }

# 执行预测
result_3d = analyze(data_3d, '3D', '2026082')
result_pl3 = analyze(data_pl3, '排列三', '2026082')
