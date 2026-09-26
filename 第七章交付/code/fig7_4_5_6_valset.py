# -*- coding: utf-8 -*-
"""图7-4 验证集典型解释案例；图7-5 三模态贡献分布；图7-6 主要贡献模态数量分布。
数据：阶段八_验证集模态贡献.csv、阶段八_验证集关键证据.csv。案例样本与 阶段八_验证集解释卡/ 三张卡一致（按规则自动选取）。"""
import numpy as np
from fig7_common import *

c = rd('阶段八_验证集模态贡献.csv')
e = rd('阶段八_验证集关键证据.csv')
c['correct'] = c.y_true_class == c.pred_class
MODS = ['文本', '音频', '视觉']; KEYS = ['text', 'audio', 'vision']

# ---------------- 图7-4 ----------------
CASES = [('-UacrmKiTn4$_$7', '文本主导典型样本'), ('ZaoFHcbRM9g$_$9', '低置信边界样本'), ('101787$_$11', '音频主导样本')]
fig, axs = plt.subplots(2, 3, figsize=(W_IN, W_IN * 0.62), gridspec_kw={'height_ratios': [0.8, 1.25], 'hspace': 0.7, 'wspace': 1.25})
for j, (sid, name) in enumerate(CASES):
    r = c[c.sample_id == sid].iloc[0]
    ax = axs[0, j]
    vals = [r[f'{k}_Δcls_raw'] for k in KEYS]
    ax.barh(range(3), vals, color=[MOD_COLOR[m] for m in MODS], height=0.6)
    for i, v in enumerate(vals):
        ax.text(max(v, 0) + 0.008, i, f'{f4(v, True)}', va='center', ha='left', fontsize=6.6)
    ax.axvline(0, color='#444', lw=0.7)
    ax.set_yticks(range(3), MODS); ax.invert_yaxis()
    ax.set_xlim(min(-0.1, min(vals) - 0.03), max(vals) + 0.17)
    ax.set_xlabel('模态分类贡献 $\\Delta^{\\mathrm{cls}}$', fontsize=7.5)
    sid_txt = sid.replace('$', r'\$')
    ax.set_title(f'({"abc"[j]}) {name}\n{sid_txt}\n真实 {POL_IDX[r.y_true_class]}｜预测 {POL_IDX[r.pred_class]}（p={f4(r.pred_prob_at_pred)}）',
                 fontsize=7.6, loc='left', x=-0.28)
    ax = axs[1, j]
    t = e[(e.sample_id == sid) & (e.modality == 'text')].sort_values('rank')
    ctxs = [x.replace(' [PAD]', '') for x in t['上下文(±3词元)']]
    labs = [f'{tok}{"*" if sw == "是" else ""}\n{cx[:30]}' for tok, sw, cx in zip(t.token, t['是否功能词'], ctxs)]
    cols = ['#3B6FB6' if d == '支持' else '#C9A227' for d in t['方向']]
    ax.barh(range(len(t)), t['Δcls'], color=cols, height=0.6)
    ax.axvline(0, color='#444', lw=0.7)
    ax.set_yticks(range(len(t)), labs, fontsize=6.2); ax.invert_yaxis()
    lim = t['Δcls'].abs().max() * 1.35
    ax.set_xlim(-lim, lim)
    ax.set_xticks([-round(lim * 0.7, 3), 0, round(lim * 0.7, 3)]); ax.tick_params(axis='x', labelsize=6.8)
    ax.set_xlabel('文本 Top-5 词元 $\\Delta^{\\mathrm{cls}}$', fontsize=7.5)
    ea = e[(e.sample_id == sid) & (e.modality != 'text')]['Δcls'].abs().max()
    ax.set_title(f'音频/视觉 Top-5 窗口 |Δcls| ≤ {f4(ea)}', fontsize=7, loc='left', x=-0.28, color=GREY)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(fc='#3B6FB6', label='支持当前预测'), Patch(fc='#C9A227', label='抑制当前预测')],
           loc='lower center', ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.1))
fig.text(0.99, -0.08, '*功能词；词元下方为 ±3 词元上下文', ha='right', fontsize=6.8, color=GREY)
save(fig, '图7-4_验证集典型解释案例')

# ---------------- 图7-5 ----------------
fig, axs = plt.subplots(1, 2, figsize=(W_IN, W_IN * 0.4), gridspec_kw={'wspace': 0.28})
for ax, (suf, lab, tag) in zip(axs, [('Δcls_raw', '分类贡献 $\\Delta^{\\mathrm{cls}}$', '(a)'), ('Δint_raw', '强度贡献 $\\Delta^{\\mathrm{int}}$', '(b)')]):
    data = [c[f'{k}_{suf}'].values for k in KEYS]
    vp = ax.violinplot(data, positions=range(3), widths=0.8, showextrema=False)
    for b, m in zip(vp['bodies'], MODS):
        b.set_facecolor(MOD_COLOR[m]); b.set_alpha(0.35); b.set_edgecolor(MOD_COLOR[m])
    bp = ax.boxplot(data, positions=range(3), widths=0.16, patch_artist=True, showfliers=False, medianprops={'color': 'k', 'lw': 0.9})
    for b, m in zip(bp['boxes'], MODS):
        b.set_facecolor(MOD_COLOR[m]); b.set_linewidth(0.6)
    ax.axhline(0, color='#444', lw=0.7, ls='--')
    top = max(np.percentile(d, 99.5) for d in data)
    for i, d in enumerate(data):
        ax.scatter(i, d.mean(), marker='D', s=12, color='white', edgecolor='k', zorder=3, lw=0.7)
        ax.text(i, top * 1.02, f'均值 {f4(d.mean(), True)}\n>0 占 {(d > 0).mean() * 100:.2f}%', ha='center', va='bottom', fontsize=6.6)
    ax.set_xticks(range(3), MODS); ax.set_ylabel(lab)
    ax.set_ylim(min(np.percentile(d, 0.5) for d in data) - 0.05, top * 1.3)
    ax.set_title(f'{tag} {"分类输出" if tag == "(a)" else "强度输出"}（n=728，◇为均值）', loc='left', x=-0.12)
save(fig, '图7-5_验证集文本音频和视觉贡献分布')

# ---------------- 图7-6 ----------------
fig, axs = plt.subplots(1, 2, figsize=(W_IN, W_IN * 0.38), gridspec_kw={'wspace': 0.32, 'width_ratios': [0.9, 1.2]})
ax = axs[0]
cnt = c['主要模态'].value_counts().reindex(MODS)
ax.bar(range(3), cnt.values, color=[MOD_COLOR[m] for m in MODS], width=0.6)
for i, v in enumerate(cnt.values):
    ax.text(i, v + 8, f'{v}\n({v / len(c) * 100:.1f}%)', ha='center', va='bottom', fontsize=7)
ax.set_xticks(range(3), MODS); ax.set_ylim(0, 720); ax.set_ylabel('样本数')
ax.set_title('(a) 主要贡献模态（argmax |Δcls|）', loc='left', x=-0.2)
ax = axs[1]
g = c.groupby('主要模态').agg(prob=('pred_prob_at_pred', 'mean'), acc=('correct', 'mean'), txt=('text_Δcls_raw', 'mean')).reindex(MODS)
xs = np.arange(3); bw = 0.26
for k, (col, lab, fc) in enumerate([('prob', '预测类别概率均值', '#8C8C8C'), ('acc', '分类准确率', '#3B6FB6'), ('txt', '文本 Δcls 均值', '#A8C0E0')]):
    ax.bar(xs + (k - 1) * bw, g[col], bw, color=fc, label=lab)
    for x, v in zip(xs + (k - 1) * bw, g[col]):
        ax.text(x, v + 0.012, f'{v:.3f}', ha='center', va='bottom', fontsize=6.0)
ax.set_xticks(xs, [f'{m}主导\n(n={cnt[m]})' for m in MODS]); ax.set_ylim(0, 0.9)
ax.legend(frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=3)
ax.set_title('(b) 按主要模态分组的置信度、准确率与文本贡献', loc='left', x=-0.12)
save(fig, '图7-6_验证集主要贡献模态数量分布')
