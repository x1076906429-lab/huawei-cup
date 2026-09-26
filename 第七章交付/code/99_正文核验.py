# -*- coding: utf-8 -*-
"""正文终检：①正文中每个小数是否能在材料包原始数据/第六章/派生表中找到；②图号、表号、式号是否连续且被引用；
③样本 ID 是否存在；④图片文件是否存在。结果写入 data/正文数值核验明细.csv 并打印汇总。"""
import os, re, glob, json
import numpy as np, pandas as pd
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
D = os.path.join(ROOT, '第七章交付')
body = open(os.path.join(D, '问题三第七章正文.md'), encoding='utf-8').read()
txt = body.split('## 本章参考文献')[0].replace('−', '-')  # 参考文献中的卷期页码、arXiv 号不属数据


def hu(v, n):
    return str(Decimal(repr(float(v))).quantize(Decimal(1).scaleb(-n), ROUND_HALF_UP))


# ---------- 数值来源池 ----------
pool = {}


def add(v, src):
    try:
        v = float(v)
    except Exception:
        return
    if not np.isfinite(v):
        return
    for n in (1, 2, 3, 4):
        for x in (v, v * 100):
            k = hu(abs(x), n)
            pool.setdefault(k, src)


for f in glob.glob(os.path.join(ROOT, '*.csv')) + glob.glob(os.path.join(D, 'data', '*.csv')):
    df = pd.read_csv(f, encoding='utf-8-sig', low_memory=False)
    num = df.select_dtypes('number')
    src = os.path.relpath(f, ROOT)
    for col in num:
        s = num[col].dropna()
        for v in pd.unique(s): add(v, src)
        for v in (s.mean(), s.median(), s.std(ddof=0), s.std(), s.min(), s.max(), s.quantile(.1), s.quantile(.9), (s > 0).mean()):
            add(v, src + ' [列统计]')
    for col in df.columns:  # 文本列中嵌入的数值（如 3.64-5.04 秒区间）
        if df[col].dtype == object:
            for v in df[col].dropna().astype(str):
                for m in re.findall(r'-?\d+\.\d+', v): add(m, src)


def walk(o, src):
    if isinstance(o, dict):
        for v in o.values(): walk(v, src)
    elif isinstance(o, list):
        for v in o: walk(v, src)
    else:
        add(o, src)


for f in glob.glob(os.path.join(ROOT, '*.json')) + [os.path.join(D, 'data', 'verified_numbers.json')]:
    walk(json.load(open(f, encoding='utf-8')), os.path.relpath(f, ROOT))
for f in glob.glob(os.path.join(ROOT, '*.md')) + glob.glob(os.path.join(ROOT, '阶段八_验证集解释卡', '*.md')):
    if os.path.basename(f) == '问题三第七章正文.md':
        continue  # 旧草稿不作来源
    for m in re.findall(r'\d+\.\d+', open(f, encoding='utf-8').read()):
        add(m, os.path.basename(f))

# 派生量（正文中由原始数据直接算出的比值、计数）
derived = {'22': '0.3002/0.0136', '18': '0.3002/0.0170', '0.28': '3.11/11', '83.2': '593/713', '83.8': '589/703',
           '18.0': '131/728', '35': '1-0.6484', '39': '1-0.6099', '40.9': '1482/3622', '47.4': '1653/3488', '47.1': '1559/3309',
           '43.0': '43/100', '0.9624': 'text_Δcls_norm 0.962358', '0.8450': 'corr(最大概率,文本Δcls)', '24.52': '稀疏性CSV'}
rows = []
for m in re.finditer(r'(?<![\w.])(\d+\.\d+)(?![\w.])', txt):
    s = m.group(1)
    ctx = txt[max(0, m.start() - 18): m.end() + 6].replace('\n', ' ')
    src = pool.get(s) or derived.get(s)
    rows.append((s, ctx, src or '未找到'))
res = pd.DataFrame(rows, columns=['正文数值', '上下文', '来源'])
res.to_csv(os.path.join(D, 'data', '正文数值核验明细.csv'), index=False, encoding='utf-8-sig')
miss = res[res['来源'] == '未找到']
print(f'正文小数共 {len(res)} 处，可溯源 {len(res) - len(miss)} 处，未找到 {len(miss)} 处')
print(miss.to_string())

# ---------- 编号与引用 ----------
figs = re.findall(r'\*\*图(7-\d+) ', body); tabs = re.findall(r'\*\*表(7-\d+) ', body); eqs = re.findall(r'\\tag\{(7-\d+)\}', body)
for name, seq in [('图', figs), ('表', tabs), ('式', eqs)]:
    nums = [int(x.split('-')[1]) for x in seq]
    print(name, seq, '连续' if nums == list(range(1, len(nums) + 1)) else '不连续！')
for f_ in figs:
    first_ref = body.find(f'图{f_}'); cap = body.find(f'**图{f_} ')
    print(f'  图{f_} 正文首次引用位置 {"先于" if first_ref < cap else "晚于"}图题')
for t_ in tabs:
    print(f'  表{t_} 引用次数', len(re.findall(f'表{t_}(?!\\d)', body)))
for e_ in eqs:
    print(f'  式({e_}) 被引用', len(re.findall(re.escape(f'式({e_})'), body)), '次')
for p in re.findall(r'\]\((figures/[^)]+)\)', body):
    print('  图片', p, '存在' if os.path.exists(os.path.join(D, p)) else '缺失！')

# ---------- 样本 ID ----------
val_ids = set(pd.read_csv(os.path.join(ROOT, '阶段八_验证集模态贡献.csv'), encoding='utf-8-sig').sample_id)
for sid in set(re.findall(r'`([^`]*\$_\$[^`]*)`', body)):
    print('  验证集样本', sid, '存在' if sid in val_ids else '不存在！')
att4 = [f'{i:02d}' for i in range(1, 21)]
bad = [x for x in re.findall(r'样本(\d{2})(?![\d%.])', body) if x not in att4]
print('  附件4 样本编号越界：', bad or '无')
