#!/usr/bin/env python3
"""测试 JSON 提取逻辑 - 使用已保存的详情页 HTML"""

import sys
import json
sys.path.insert(0, '/Users/qinxiaoqiang/Downloads/chinadrugtrials')

from bs4 import BeautifulSoup, Tag
from pathlib import Path

# 读取已保存的详情页 HTML
html_path = Path('/Users/qinxiaoqiang/Downloads/chinadrugtrials/output/胰腺癌/raw/CTR20260151_detail.html')
html = html_path.read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')

# 查找 paddingSide15 div
content_div = soup.find('div', class_='paddingSide15')
print(f"找到 paddingSide15 div: {content_div is not None}")

if content_div:
    # 提取结构化数据
    data = {
        'reg_no': 'CTR20260151',
        'details': {},
        'sections': {},
    }

    current_section = '基本信息'
    data['sections'][current_section] = {}

    def extract_table_kv(table, data_dict):
        for row in table.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            if len(cells) < 2:
                continue
            if len(cells) == 2:
                key = cells[0].get_text(strip=True).rstrip('：: ')
                val = cells[1].get_text(strip=True)
                if key and val and key not in ('序号',):
                    data_dict[key] = val
            elif len(cells) >= 4 and len(cells) % 2 == 0:
                for i in range(0, len(cells), 2):
                    key = cells[i].get_text(strip=True).rstrip('：: ')
                    val = cells[i + 1].get_text(strip=True) if i + 1 < len(cells) else ''
                    if key and val:
                        data_dict[key] = val

    for elem in content_div.descendants:
        if not isinstance(elem, Tag):
            continue

        if elem.name in ('h2', 'h3', 'h4', 'h5'):
            text = elem.get_text(strip=True)
            if text and len(text) < 50:
                current_section = text
                data['sections'].setdefault(current_section, {})

        elif elem.get('class') and 'searchDetailPartTit' in elem.get('class', []):
            text = elem.get_text(strip=True)
            if text and len(text) < 80:
                current_section = text
                data['sections'].setdefault(current_section, {})

        elif elem.get('class') and 'sDPTit2' in elem.get('class', []):
            text = elem.get_text(strip=True)
            if text and len(text) < 80:
                current_section = text
                data['sections'].setdefault(current_section, {})

        elif elem.name == 'table':
            if elem.find_parent('table') is None:
                section_data = data['sections'].setdefault(current_section, {})
                extract_table_kv(elem, section_data)
                extract_table_kv(elem, data['details'])

    # 输出结果
    print(f"\n=== 提取到的字段数: {len(data['details'])} ===")
    print(f"\n=== 详情字段 (前20个) ===")
    for i, (k, v) in enumerate(list(data['details'].items())[:20]):
        print(f"  {k}: {v[:60]}{'...' if len(v) > 60 else ''}")

    print(f"\n=== 分区结构 ({len(data['sections'])} 个分区) ===")
    for section, fields in data['sections'].items():
        if fields:
            print(f"  [{section}] ({len(fields)} 个字段)")
            for k in list(fields.keys())[:3]:
                print(f"    - {k}")
            if len(fields) > 3:
                print(f"    ... 共 {len(fields)} 个字段")

    # 保存测试结果
    out_path = Path('/Users/qinxiaoqiang/Downloads/chinadrugtrials/output/test_json_extraction.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n测试结果已保存: {out_path}")
