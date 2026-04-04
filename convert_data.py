import json

def convert_3d():
    records = []
    with open(r'C:\Users\zhao\Desktop\3d.txt', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5 and parts[0].startswith('20'):
                period = parts[0]
                date = parts[1]
                # 格式: 期号 日期 百 十 个
                number = parts[2] + parts[3] + parts[4]
                records.append({
                    'period': period,
                    'date': date,
                    'type': '3d',
                    'number': number
                })
    return records

def convert_pl3():
    records = []
    with open(r'C:\Users\zhao\Desktop\pl3.txt', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5 and parts[0].startswith('20'):
                period = parts[0]
                date = parts[1]
                # 格式: 期号 日期 百 十 个
                number = parts[2] + parts[3] + parts[4]
                records.append({
                    'period': period,
                    'date': date,
                    'type': 'pl3',
                    'number': number
                })
    return records

# 转换数据
print('转换3d数据...')
d3_records = convert_3d()
print(f'3d: {len(d3_records)} 条')

print('转换pl3数据...')
pl3_records = convert_pl3()
print(f'pl3: {len(pl3_records)} 条')

# 合并并按期号降序排序
all_records = d3_records + pl3_records
all_records.sort(key=lambda x: x['period'], reverse=True)

print(f'总计: {len(all_records)} 条')
print(f'最新: {all_records[0]["period"]} - {all_records[0]["type"]} - {all_records[0]["number"]}')

# 保存
output_path = r'c:\Users\zhao\WorkBuddy\Claw\data\all_history.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_records, f, ensure_ascii=False, indent=2)
print(f'已保存到: {output_path}')

# 检查文件大小
import os
size = os.path.getsize(output_path)
print(f'文件大小: {size/1024:.1f} KB')