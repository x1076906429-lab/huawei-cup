# -*- coding: utf-8 -*-
"""图7-1 多模态解释方法与遮蔽流程示意图（常量取自 阶段八_解释方法配置.json）。"""
import json, os
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from fig7_common import *

cfg = json.load(open(os.path.join(ROOT, '阶段八_解释方法配置.json'), encoding='utf-8'))
W = cfg['frozen_constants']['window_length']
K = cfg['frozen_constants']['top_k']

fig = plt.figure(figsize=(W_IN, W_IN * 0.74))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 74); ax.axis('off')


def box(x, y, w, h, text, fc='#FFFFFF', ec='#5A5A5A', fs=8, lw=0.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=1.2', fc=fc, ec=ec, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, linespacing=1.4)


def arrow(x1, y1, x2, y2, c='#5A5A5A'):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=9, color=c, lw=0.9))


def title(x, y, s):
    ax.text(x, y, s, fontsize=9, fontweight='bold', va='bottom')


# ① 输入与冻结模型
title(1, 70, '① 冻结模型与完整输入')
for i, (m, shape) in enumerate([('文本', '50×768'), ('音频', '50×74'), ('视觉', '50×35')]):
    box(1, 61 - i * 6.6, 17, 5.6, f'{m}  {shape}\n+ 观测掩码', fc=MOD_COLOR[m] + '22', ec=MOD_COLOR[m], fs=7)
    arrow(18.2, 63.7 - i * 6.6, 22.3, 58.5)
box(22.5, 52, 16, 13.5, '问题二冻结模型\nstatic_concat\n81,540 参数\neval + no_grad', fc='#F4F4F4', fs=7.8)
arrow(38.7, 58.7, 42.3, 58.7)
box(42.5, 53.5, 17, 10.5, '完整输入输出\n$p^{\\mathrm{full}}(\\hat y)$\n$\\hat r^{\\mathrm{full}}$', fc='#FFFFFF', fs=7.8)

# ② 模态级遮蔽
title(64, 70, '② 模态级遮蔽')
box(64, 54.5, 35, 15, '模态 $m$ 的观测掩码整体置无效、输入置零\n得到 $p^{(-m)}(\\hat y)$ 与 $\\hat r^{(-m)}$\n计算 $\\Delta^{\\mathrm{cls}}_m$、$\\Delta^{\\mathrm{int}}_m$ 并样本内归一化\n主要模态 $=\\arg\\max_m|\\Delta^{\\mathrm{cls}}_m|$',
    fc='#FFF8EC', ec='#C98A2B', fs=7.4)
arrow(59.7, 60, 63.8, 61.5)

# ③ 位置级遮蔽
title(64, 49, '③ 位置级遮蔽')
box(64, 33.5, 35, 15, f'文本：单个词元位置，步长 1\n音频/视觉：连续窗口 W={W}，步长 1\n仅对已观测单元计算 $\\Delta^{{\\mathrm{{cls}}}}$\n按 $|\\Delta^{{\\mathrm{{cls}}}}|$ 降序取 Top-{K}（对照 K=3）',
    fc='#FFF8EC', ec='#C98A2B', fs=7.4)
arrow(59.7, 55, 63.8, 44)

# ④ 证据映射
title(1, 44, '④ 关键证据与原始位置映射')
box(1, 26, 18.5, 16.5, '文本\n词元序号 + 词元\n±3 词元上下文\n功能词标记', fc=MOD_COLOR['文本'] + '1A', ec=MOD_COLOR['文本'], fs=7.4)
box(21.5, 26, 18.5, 16.5, '音频\n桶位区间\n→ 视频内重建秒数', fc=MOD_COLOR['音频'] + '1A', ec=MOD_COLOR['音频'], fs=7.4)
box(42, 26, 18.5, 16.5, '视觉\n桶位区间 → 重建秒数\n→ 帧号 round(30t)\n→ 关键帧截图', fc=MOD_COLOR['视觉'] + '1A', ec=MOD_COLOR['视觉'], fs=7.4)
arrow(63.8, 38, 60.8, 36)
ax.text(1, 16.5, '附件2 无时长/帧率字段：音频、视觉只给桶位与相对位置；\n附件4 带原始视频：按有效跨度线性重建时间与帧号（近似值）',
        fontsize=7, color=GREY)

# ⑤ 验证
title(64, 28, '⑤ 解释验证（附件2 验证集，n=728）')
box(64, 13, 17, 13.5, '忠实度\nTop-K 片段\nvs 等长随机片段\n（随机重复 10 次）', fc='#EEF3FA', ec='#3B6FB6', fs=7.2)
box(82, 13, 17, 13.5, '稳定性\n窗口平移 ±1\n输入扰动\nσ ∈ {0.01, 0.1, 0.5}', fc='#EEF3FA', ec='#3B6FB6', fs=7.2)

# 边界说明
box(1, 1.5, 98, 8, '贡献为相对遮蔽基线的边际效应，不等同于因果贡献；三模态贡献不可加；时间与帧号为重建的近似位置；\n'
    '全部结果基于单份冻结权重（主种子 20260924），不含跨训练种子的变化', fc='#F7F7F7', ec='#BBBBBB', fs=7.2)

save(fig, '图7-1_多模态解释方法与遮蔽流程示意图')
