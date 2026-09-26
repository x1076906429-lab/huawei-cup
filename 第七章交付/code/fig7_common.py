# -*- coding: utf-8 -*-
"""第七章图表统一样式与数据读取。

字体：绘图阶段统一使用文泉驿正黑保证中文显示；终稿排版时将 FONT_CN / FONT_EN
改为 ['SimSun'] / ['Times New Roman']（或黑体）后重新运行 fig7_all.py 即可整体替换。
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, '第七章交付', 'figures')
os.makedirs(OUT, exist_ok=True)

FONT_CN = ['WenQuanYi Zen Hei']   # 终稿：['SimSun'] 或 ['SimHei']
FONT_EN = []                       # 终稿：['Times New Roman']（放在 FONT_CN 之前）
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': FONT_EN + FONT_CN + ['DejaVu Sans'],
    'axes.unicode_minus': False,
    'font.size': 9, 'axes.titlesize': 9.5, 'axes.labelsize': 9,
    'xtick.labelsize': 8, 'ytick.labelsize': 8, 'legend.fontsize': 8,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.linewidth': 0.7, 'axes.grid': True, 'grid.color': '#E3E3E3', 'grid.linewidth': 0.6,
    'axes.axisbelow': True, 'savefig.dpi': 300, 'figure.dpi': 110,
    'svg.fonttype': 'none', 'pdf.fonttype': 42,
})

W_CM = 16.0
W_IN = W_CM / 2.54

# 三模态固定配色；三类极性固定配色（全章一致）
MOD_COLOR = {'文本': '#3B6FB6', '音频': '#E0892B', '视觉': '#4E9F50'}
MOD_EN = {'text': '文本', 'audio': '音频', 'vision': '视觉'}
POL_COLOR = {'负向': '#C44E52', '中性': '#9E9E9E', '正向': '#8172B3'}
POL_EN = {'negative': '负向', 'neutral': '中性', 'positive': '正向'}
POL_IDX = {0: '负向', 1: '中性', 2: '正向'}
GREY = '#6B6B6B'
REVIEW_SHORT = {'人工回看支持': '支持', '部分支持': '部分支持', '不支持': '不支持', '无法确认': '无法确认'}


def rd(name, **kw):
    return pd.read_csv(os.path.join(ROOT, name), encoding='utf-8-sig', **kw)


def save(fig, stem):
    for ext in ('png', 'svg', 'pdf'):
        fig.savefig(os.path.join(OUT, f'{stem}.{ext}'), bbox_inches='tight')
    plt.close(fig)
    print('saved', stem)


def panel_label(ax, s, x=-0.12, y=1.04):
    ax.text(x, y, s, transform=ax.transAxes, fontsize=10, fontweight='bold', va='bottom', ha='left')


from decimal import Decimal, ROUND_HALF_UP


def f4(v, sign=False):
    """四位小数，ROUND_HALF_UP（与正文表格一致）；sign=True 时带正负号。"""
    d = Decimal(repr(float(v))).quantize(Decimal('0.0001'), ROUND_HALF_UP)
    return (f'{d:+}' if sign else f'{d}').replace('-0.0000', '0.0000').replace('+-', '-')
