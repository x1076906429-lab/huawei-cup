# -*- coding: utf-8 -*-
"""图7-2 忠实度（阶段八_解释忠实度验证.csv）；图7-3 稳定性（阶段八_解释稳定性验证.csv + 配置 JSON）。"""
import json, os
import numpy as np
from fig7_common import *

# ---------------- 图7-2 ----------------
f = rd('阶段八_解释忠实度验证.csv')
C_TOP, C_RND = '#3B6FB6', '#B5B5B5'


def ci95(x):
    x = np.asarray(x, float)
    return 1.96 * x.std(ddof=1) / np.sqrt(len(x))


fig, axs = plt.subplots(1, 3, figsize=(W_IN, W_IN * 0.42), gridspec_kw={'width_ratios': [1.1, 0.9, 1.1], 'wspace': 0.5})
ks = [3, 5]; xs = np.array([0, 1.25]); bw = 0.4
ax = axs[0]
for j, (col, lab, c) in enumerate([('ΔP_topK', 'Top-K 重要片段', C_TOP), ('ΔP_random_mean', '等长随机片段', C_RND)]):
    m = [f[f.K == k][col].mean() for k in ks]; e = [ci95(f[f.K == k][col]) for k in ks]
    ax.bar(xs + (j - .5) * bw, m, bw, yerr=e, color=c, capsize=2.5, error_kw={'lw': 0.8}, label=lab)
    for x, v in zip(xs + (j - .5) * bw, m):
        ax.text(x + bw * 0.52, v / 2, f'{f4(v, True)}', ha='left', va='center', fontsize=6.0, rotation=90) if False else None
    for x, v, ee in zip(xs + (j - .5) * bw, m, e):
        ax.text(x, v + ee + 0.001 if v > 0 else v - ee - 0.001, f'{f4(v, True)}', ha='center', va='bottom' if v > 0 else 'top', fontsize=6.4)
for x, k in zip(xs, ks):
    g = f[f.K == k]
    ax.text(x, 0.053, f'配对差\n{f4(g["ΔP_差(重要-随机)"].mean(), True)}\nn={len(g)}', ha='center', fontsize=6.4, color='#333')
ax.axhline(0, color='#555', lw=0.7)
ax.set_xticks(xs, [f'K={k}' for k in ks]); ax.set_ylim(-0.015, 0.075)
ax.set_ylabel('预测类别概率下降 ΔP'); ax.set_title('(a) 置信度下降（均值±95%CI）', loc='left', x=-0.25)
ax.legend(loc='upper left', frameon=False, bbox_to_anchor=(0, -0.13), ncol=1)

ax = axs[1]
top = [f[f.K == k]['预测翻转_topK'].mean() * 100 for k in ks]
rnd = [f[f.K == k]['预测翻转率_random'].mean() * 100 for k in ks]
ax.bar(xs - bw / 2, top, bw, color=C_TOP); ax.bar(xs + bw / 2, rnd, bw, color=C_RND)
for x, v in zip(list(xs - bw / 2) + list(xs + bw / 2), top + rnd):
    ax.text(x, v + 0.15, f'{v:.2f}', ha='center', va='bottom', fontsize=5.8)
ax.set_xticks(xs, [f'K={k}' for k in ks]); ax.set_ylim(0, 10)
ax.set_ylabel('类别翻转率 / %'); ax.set_ylim(0, 9.5); ax.set_title('(b) 类别翻转率 / %', loc='left', x=-0.25)

ax = axs[2]
data, pos, cols = [], [], []
for i, k in enumerate(ks):
    g = f[f.K == k]
    for j, fl in enumerate([1, 0]):
        data.append(g[g['预测翻转_topK'] == fl].pred_prob_at_pred.values); pos.append(i * 2.4 + j); cols.append('#C44E52' if fl else '#8FA9CF')
bp = ax.boxplot(data, positions=pos, widths=0.7, patch_artist=True, showfliers=False, medianprops={'color': 'k', 'lw': 0.9})
for b, c in zip(bp['boxes'], cols):
    b.set_facecolor(c); b.set_alpha(0.75); b.set_linewidth(0.6)
for p_, d in zip(pos, data):
    ax.scatter(p_, d.mean(), marker='D', s=10, color='k', zorder=3)
    ax.text(p_, 1.02, f'{d.mean():.3f}', ha='center', fontsize=6.2)
ax.set_xticks([0.5, 2.9], [f'K={k}' for k in ks]); ax.set_ylim(0.3, 1.08)
ax.set_ylabel('预测类别概率'); ax.set_title('(c) 完整输入置信度（◆为均值）', loc='left', x=-0.25)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(fc='#C44E52', alpha=.75, label='Top-K 遮蔽后翻转'), Patch(fc='#8FA9CF', alpha=.75, label='未翻转')],
          frameon=False, loc='upper left', bbox_to_anchor=(0, -0.13), ncol=1)
save(fig, '图7-2_Top-K重要片段与随机片段的忠实度比较')

# ---------------- 图7-3 ----------------
s = rd('阶段八_解释稳定性验证.csv')
cfg = json.load(open(os.path.join(ROOT, '阶段八_解释方法配置.json'), encoding='utf-8'))
st = cfg['validation_summary']['stability']
fig, axs = plt.subplots(1, 2, figsize=(W_IN, W_IN * 0.38), gridspec_kw={'width_ratios': [1.35, 1], 'wspace': 0.32})
ax = axs[0]
groups = [('audio', '-1'), ('audio', '+1'), ('vision', '-1'), ('vision', '+1')]
xs = np.arange(len(groups)); bw = 0.36
for j, (metric, lab, hatch) in enumerate([('spearman', '位置重要性 Spearman', ''), ('top5_overlap', 'Top-5 重合率', '///')]):
    for i, (m, sh) in enumerate(groups):
        v = s[f'{m}_{metric}_shift{sh}']
        c = MOD_COLOR[MOD_EN[m]]
        ax.bar(i + (j - .5) * bw, v.mean(), bw, color=c, alpha=0.9 if j == 0 else 0.45, hatch=hatch, edgecolor='white', lw=0.3,
               label=lab if i == 0 else None)
        q1, q3 = v.quantile(.25), v.quantile(.75)
        ax.text(i + (j - .5) * bw, 1.005, f'{f4(v.mean())}', ha='center', va='bottom', fontsize=6.2, rotation=90)
ax.set_xticks(xs, ['音频 -1', '音频 +1', '视觉 -1', '视觉 +1'])
ax.set_ylim(0.85, 1.075); ax.set_ylabel('一致性（728 条样本均值）')
from matplotlib.patches import Patch
ax.legend(handles=[Patch(fc='#888', label='位置重要性 Spearman'), Patch(fc='#888', alpha=.45, hatch='///', ec='white', label='Top-5 重合率')],
          frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2)
ax.set_title('(a) 窗口整体平移 ±1 个桶位', loc='left', x=-0.12)

ax = axs[1]
sig = [0.01, 0.1, 0.5]
sa = [st['noise_sign_agreement'][str(x)] for x in sig]
rs = [st['noise_rank_spearman'][str(x)] for x in sig]
# 交叉核对：CSV 中与 JSON 同名的列必须一致
for x, v in zip(sig, sa):
    assert abs(s[f'扰动σ{x}_符号一致率'].iloc[0] - v) < 1e-4
assert abs(s['扰动σ0.5_排名Spearman'].iloc[0] - rs[-1]) < 1e-4
ax.plot(range(3), sa, '-o', color='#3B6FB6', ms=4, lw=1.2, label='三模态贡献符号一致率')
ax.plot(range(3), rs, '-s', color='#C44E52', ms=4, lw=1.2, label='样本内模态排名 Spearman')
for i in range(3):
    ax.text(i, sa[i] + 0.004, f'{f4(sa[i])}', ha='center', va='bottom', fontsize=6.8, color='#3B6FB6')
    ax.text(i + 0.07, rs[i] - 0.002, f'{f4(rs[i])}', ha='left', va='top', fontsize=6.8, color='#C44E52')
ax.set_xticks(range(3), [f'σ={x}' for x in sig]); ax.set_xlim(-0.4, 2.4)
ax.set_ylim(0.92, 1.012); ax.set_ylabel('一致性')
ax.set_title('(b) 已观测位置叠加高斯扰动', loc='left', x=-0.2)
ax.legend(frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1)
save(fig, '图7-3_窗口平移与输入扰动下的解释稳定性')
