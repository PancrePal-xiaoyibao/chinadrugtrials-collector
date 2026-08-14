#!/usr/bin/env python3
"""测试列表页解析逻辑 - 使用用户提供的 HTML 片段"""

import sys
sys.path.insert(0, '/Users/qinxiaoqiang/Downloads/chinadrugtrials')

from bs4 import BeautifulSoup
from scraper import ChinaDrugTrialsScraper

# 用户提供的列表页 HTML 片段（关键部分）
SAMPLE_HTML = '''
<div class="paddingSide15">
    <table border="0" cellspacing="0" cellpadding="0" class="searchTable">
            <tr class="Tab_title">
                <th width="7%" height="42" >序号</th>
                <th width="17%" >登记号</th>
                <th width="17%" >试验状态</th>
                <th width="18%" >药物名称</th>
                <th width="21%" >适应症</th>
                <th width="20%" >试验通俗题目</th>
            </tr>
                <tr style=" color:#535353">
                <td height="40" >&nbsp;1</td>
                <td >
                    <a href="javascript:void(0)" onclick="getDetail(this.id)" id="ef63809598474afd9e150fd43b633aee" name="1">
                        CTR20260151
                    </a></td>
                <td >
                    <a href="javascript:void(0)" onclick="getDetail(this.id)" id="ef63809598474afd9e150fd43b633aee" name="1">
                        进行中&nbsp;招募中
                    </a>
                </td>
                <td >
                    <a href="javascript:void(0)" onclick="getDetail(this.id)" id="ef63809598474afd9e150fd43b633aee" name="1">
                        Ponsegromab注射液
                    </a>
                </td>
                <td ><a href="javascript:void(0)" onclick="getDetail(this.id)" id="ef63809598474afd9e150fd43b633aee" name="1">胰腺癌恶病质</a></td>
                <td ><a href="javascript:void(0)" onclick="getDetail(this.id)" id="ef63809598474afd9e150fd43b633aee" name="1">一项在已转移并导致显著体重下降的胰腺癌成人研究参与者中评估药物Ponsegromab 的研究</a></td>
                </tr>
                <tr style=" color:#535353">
                <td height="40" >&nbsp;2</td>
                <td >
                    <a href="javascript:void(0)" onclick="getDetail(this.id)" id="4d1ea7bc0caa4ffdb76d249b4b1536d8" name="2">
                        CTR20254276
                    </a></td>
                <td >
                    <a href="javascript:void(0)" onclick="getDetail(this.id)" id="4d1ea7bc0caa4ffdb76d249b4b1536d8" name="2">
                        进行中&nbsp;招募中
                    </a>
                </td>
                <td >
                    <a href="javascript:void(0)" onclick="getDetail(this.id)" id="4d1ea7bc0caa4ffdb76d249b4b1536d8" name="2">
                        盐酸伊立替康脂质体注射液(II)
                    </a>
                </td>
                <td ><a href="javascript:void(0)" onclick="getDetail(this.id)" id="4d1ea7bc0caa4ffdb76d249b4b1536d8" name="2">转移性胰腺癌</a></td>
                <td ><a href="javascript:void(0)" onclick="getDetail(this.id)" id="4d1ea7bc0caa4ffdb76d249b4b1536d8" name="2">盐酸伊立替康脂质体注射液(II) 联合奥沙利铂、5-FU/LV对比白蛋白紫杉醇联合吉西他滨一线治疗晚期胰腺癌的临床研究</a></td>
                </tr>
                <tr style=" color:#535353">
                <td height="40" >&nbsp;17</td>
                <td >
                    <a href="javascript:void(0)" onclick="getDetail(this.id)" id="3bcae82b086b432d96d909bcc557883f_p" name="17">
                        CTR20192634
                    </a></td>
                <td >
                    <a href="javascript:void(0)" onclick="getDetail(this.id)" id="3bcae82b086b432d96d909bcc557883f_p" name="17">
                        进行中&nbsp;招募中
                    </a>
                </td>
                <td >
                    <a href="javascript:void(0)" onclick="getDetail(this.id)" id="3bcae82b086b432d96d909bcc557883f_p" name="17">
                        氟唑帕利胶囊
                    </a>
                </td>
                <td ><a href="javascript:void(0)" onclick="getDetail(this.id)" id="3bcae82b086b432d96d909bcc557883f_p" name="17">晚期胰腺癌</a></td>
                <td ><a href="javascript:void(0)" onclick="getDetail(this.id)" id="3bcae82b086b432d96d909bcc557883f_p" name="17">氟唑帕利胶囊联合化疗治疗晚期胰腺癌的Ib/II期临床研究</a></td>
                </tr>
    </table>
</div>
<div class="">
    <div class="pull-right pageInfo">
     跳转到 <input type="text" onKeyPress="if(event.keyCode==13) gotopage(this.value)"> 页
    &nbsp;&nbsp;
    当前第 <i>1</i> 页，共 <i>3</i> 页，共 <i>58</i> 条记录
  </div>
  <ul class="pagination">
            <li class="active"><a href="#"  onclick="gotopage(1)">1 <span class="sr-only">(current)</span></a></li>
            <li><a href="#" onclick="gotopage(2)">2</a></li>
            <li><a href="#" onclick="gotopage(3)">3</a></li>
            <li><a href="#" onclick="gotopage(2);" aria-label="Next"><span aria-hidden="true">»</span></a></li>
    </ul>
</div>
'''

# 模拟解析
soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')

# 测试分页解析
# 直接调用方法（不实例化完整对象，避免需要 cookies）
import re

page_info = soup.find('div', class_='pageInfo')
text = page_info.get_text()
print("=== 分页信息测试 ===")
print(f"原始文本: {text.strip()}")

m = re.search(r'当前第\s*(\d+)\s*页.*?共\s*(\d+)\s*页.*?共\s*(\d+)\s*条', text)
if m:
    print(f"正则匹配: 当前第 {m.group(1)} 页, 共 {m.group(2)} 页, 共 {m.group(3)} 条记录")
else:
    print("正则匹配失败!")
    i_tags = page_info.find_all('i')
    if len(i_tags) >= 3:
        print(f"<i>标签: {i_tags[0].text}, {i_tags[1].text}, {i_tags[2].text}")

# 测试列表解析
print("\n=== 试验列表解析测试 ===")
table = soup.find('table', class_='searchTable')
rows = table.find_all('tr')
print(f"总行数(含标题): {len(rows)}")

trial_count = 0
for row in rows[1:]:  # 跳过标题行
    cells = row.find_all('td')
    if len(cells) < 6:
        continue
    
    link = cells[1].find('a')
    if not link:
        continue
    
    trial = {
        'seq':        cells[0].get_text(strip=True).replace('\xa0', ''),
        'id':         link.get('id', ''),
        'ckm_index':  link.get('name', ''),
        'reg_no':     cells[1].get_text(strip=True),
        'state':      cells[2].get_text(strip=True).replace('\xa0', ' '),
        'drug_name':  cells[3].get_text(strip=True),
        'indication': cells[4].get_text(strip=True),
        'title':      cells[5].get_text(strip=True),
    }
    trial_count += 1
    print(f"\n--- 试验 {trial_count} ---")
    for k, v in trial.items():
        print(f"  {k}: {v}")

print(f"\n共解析出 {trial_count} 条试验记录")

# 测试 _p 后缀的 id
print("\n=== ID 后缀测试 ===")
for row in rows[1:]:
    cells = row.find_all('td')
    if len(cells) < 6:
        continue
    link = cells[1].find('a')
    if link:
        tid = link.get('id', '')
        if '_p' in tid:
            print(f"  带 _p 后缀的 ID: {tid} (正常处理)")

# 测试表单构建
print("\n=== 表单构建测试 ===")
# 模拟构建
keywords = "胰腺癌"
form = {
    'keywords':     keywords,
    'sort':         'desc',
    'sort2':        '',
    'rule':         'CTR',
    'secondLevel':  '1',
    'currentpage':  '1',
    'id':           '',
    'ckm_index':    '',
}
print(f"基本搜索表单: {form}")

form_advanced = form.copy()
form_advanced['secondLevel'] = '0'
form_advanced['state'] = '招募中'
form_advanced['drugs_type'] = '2'
print(f"高级搜索表单: {form_advanced}")

print("\n=== 测试完成 ===")
