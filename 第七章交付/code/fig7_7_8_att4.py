# -*- coding: utf-8 -*-
"""图7-7 附件4 预测类别与置信度分布；图7-8 附件4 典型样本关键证据回看图。
数据：q3_attachment4_predictions_explanations.csv、阶段九_附件4关键证据明细.csv、关键帧/。
附件4 无标签：图中类别均为模型预测，不是真实类别。"""
import os, glob, re
import numpy as np
import matplotlib.image as mpimg
from matplotlib.patches import Patch, Rectangle
from fig7_common import *

p = rd('q3_attachment4_predictions_explanations.csv', dtype={'sample_id': str})
ev = rd('阶段九_附件4关键证据明细.csv', dtype={'sample_id': str})
P = p[['prob_neg', 'prob_neu', 'prob_pos']].values
p['maxp'] = P.max(1); srt = np.sort(P, 1); p['gap'] = srt[:, 2] - srt[:, 1]
p['pol'] = p.pred_annotation.map(POL_EN)

# ---------------- 图7-7 ----------------
fig, axs = plt.subplots(1, 2, figsize=(W_IN, W_IN * 0.5), gridspec_kw={'width_ratios': [0.62, 1.6], 'wspace': 0.3})
ax = axs[0]
order = ['负向', '中性', '正向']
cnt = p.pol.value_counts().reindex(order).fillna(0).astype(int)
ax.bar(range(3), cnt.values, color=[POL_COLOR[o] for o in order], width=0.6)
for i, v in enumerate(cnt.values):
    ax.text(i, v + 0.2, f'{v}', ha='center', va='bottom', fontsize=8)
ax.set_xticks(range(3), order); ax.set_ylim(0, 15); ax.set_ylabel('样本数（预测类别）')
ax.set_title('(a) 预测类别（n=20）', loc='left', x=-0.3)

ax = axs[1]
q = p.sort_values('maxp', ascending=True).reset_index(drop=True)
left = np.zeros(len(q))
for col, o in zip(['prob_neg', 'prob_neu', 'prob_pos'], order):
    ax.barh(range(len(q)), q[col], left=left, color=POL_COLOR[o], height=0.72, label=f'{o}概率')
    left += q[col].values
ax.axvline(0.5, color='k', lw=0.7, ls='--')
MARK = {'人工回看支持': '支持', '部分支持': '部分支持', '不支持': '不支持', '无法确认': '无法确认'}
for i, r in q.iterrows():
    ax.text(1.015, i, f'{f4(r.maxp)}  {MARK[r["AI辅助回看判定"]]}', va='center', fontsize=6.6)
ax.set_yticks(range(len(q)), [f'{s}（{a}）' for s, a in zip(q.sample_id, q.pol)], fontsize=6.8)
ax.set_xlim(0, 1); ax.set_xlabel('三类预测概率（按最大类别概率升序排列）')
ax.text(1.015, len(q) - 0.2, '最大概率  回看', fontsize=6.6, va='bottom', color=GREY)
ax.grid(axis='y', visible=False)
ax.legend(frameon=False, loc='upper center', bbox_to_anchor=(0.45, -0.16), ncol=3)
ax.set_title('(b) 逐样本三类概率（虚线为 0.5）', loc='left', x=-0.18)
fig.text(0.99, -0.1, '回看结论：AI 辅助回看，经人工逐条复核确认', ha='right', fontsize=6.6, color=GREY)
save(fig, '图7-7_附件4预测类别与置信度分布')

# ---------------- 图7-8 ----------------
CASES = [('09', '文本主导、高置信'), ('02', '低置信边界'), ('14', '视觉主导')]
fig = plt.figure(figsize=(W_IN, W_IN * 1.2))
outer = fig.add_gridspec(len(CASES), 1, hspace=0.42)
for i, (sid, name) in enumerate(CASES):
    r = p[p.sample_id == sid].iloc[0]; e = ev[ev.sample_id == sid]
    dur = float(r.duration_s)
    g = outer[i].subgridspec(2, 3, height_ratios=[0.2, 1], width_ratios=[1.0, 1.3, 1.25], wspace=0.28, hspace=0.05)
    hx = fig.add_subplot(g[0, :]); hx.axis('off')
    hx.text(0, 0.5, f'({"abc"[i]}) 样本 {sid}（{name}）：预测 {r.pol}，负/中/正概率 {f4(r.prob_neg)}/{f4(r.prob_neu)}/{f4(r.prob_pos)}，'
            f'强度 {f4(r.pred_intensity, True)}\n     模态贡献 文本 {f4(r.text_contribution, True)}｜音频 {f4(r.audio_contribution, True)}｜'
            f'视觉 {f4(r.vision_contribution, True)}；主要模态 {r.dominant_modality}；回看结论 {REVIEW_SHORT[r["AI辅助回看判定"]]}',
            fontsize=7.2, va='center', ha='left', transform=hx.transAxes)
    # 关键帧
    ax = fig.add_subplot(g[1, 0])
    kfs = sorted(glob.glob(os.path.join(ROOT, '关键帧', sid, 'kp1_*.png')))
    ax.imshow(mpimg.imread(kfs[0])); ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for sp in ax.spines.values(): sp.set_visible(True); sp.set_color('#999')
    t_kp = float(re.search(r't([\d.]+)s', kfs[0]).group(1))
    ax.set_xlabel(f'视觉 rank-1 窗口中点帧 t≈{t_kp:.2f} s（帧≈{round(t_kp * 30)}）', fontsize=6.5)
    # 时间轴
    ax = fig.add_subplot(g[1, 1])
    info = []
    for row, (mod, lab) in enumerate([('vision', '视觉'), ('audio', '音频')]):
        sub = e[e.modality == mod].dropna(subset=['start_sec']).sort_values('rank', ascending=False)
        for _, s_ in sub.iterrows():
            a = 0.9 if s_['rank'] == 1 else 0.25
            ax.add_patch(Rectangle((s_.start_sec, row + 0.15), s_.end_sec - s_.start_sec, 0.7, fc=MOD_COLOR[lab], alpha=a, lw=0))
        s1 = sub[sub['rank'] == 1].iloc[0]
        info.append(f'{lab} rank-1：{s1.start_sec:.2f}–{s1.end_sec:.2f} s，Δcls {f4(s1.delta_cls, True)}')
    ax.axvline(t_kp, color='k', lw=0.8, ls=':')
    ax.set_xlim(0, dur); ax.set_ylim(0, 2); ax.set_yticks([0.5, 1.5], ['视觉', '音频'], fontsize=7)
    ax.tick_params(axis='x', labelsize=7); ax.grid(axis='y', visible=False)
    ax.set_xlabel('重建时间 / s（深色=rank-1，点线=关键帧时刻）\n' + '\n'.join(info[::-1]), fontsize=6.3)
    # 文本证据
    ax = fig.add_subplot(g[1, 2]); ax.axis('off')
    t = e[e.modality == 'text'].sort_values('rank')
    lines = ['文本 Top-5 词元（*功能词）与 ±3 上下文']
    for _, s_ in t.iterrows():
        ctx = str(s_.context_pm3).replace(' [PAD]', '')
        lines.append(f'{int(s_["rank"])}. {s_.token}{"*" if s_.is_stopword == "是" else ""}  {f4(s_.delta_cls, True)}')
        lines.append(f'    {ctx[:34]}')
    ax.text(0.0, 1.0, '\n'.join(lines), fontsize=6.1, va='top', ha='left', transform=ax.transAxes, linespacing=1.3)
fig.legend(handles=[Patch(fc=MOD_COLOR['音频'], label='音频 Top-5 关键窗口'), Patch(fc=MOD_COLOR['视觉'], label='视觉 Top-5 关键窗口')],
           loc='upper center', ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.045))
save(fig, '图7-8_附件4典型样本关键证据回看图')
