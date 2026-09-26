# -*- coding: utf-8 -*-
"""生成正文表7-1~表7-6 的数据表（CSV，UTF-8-BOM，可直接用 Excel/Word 打开）。"""
import json, os
import numpy as np, pandas as pd
from scipy.stats import wilcoxon

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, '第七章交付', 'data'); os.makedirs(OUT, exist_ok=True)
rd = lambda f, **k: pd.read_csv(os.path.join(ROOT, f), encoding='utf-8-sig', **k)
w = lambda df, n: (df.to_csv(os.path.join(OUT, n), index=False, encoding='utf-8-sig'), print('saved', n))
cfg = json.load(open(os.path.join(ROOT, '阶段八_解释方法配置.json'), encoding='utf-8'))
fc = cfg['frozen_constants']; mb = cfg['model_binding']

# 表7-1 解释计算设置
w(pd.DataFrame([
    ('被解释模型', f"问题二冻结 static_concat，{mb['param_count']:,} 参数，主种子 {mb['seed']}", '阶段八_解释方法配置.json / 第六章 6.1.3'),
    ('推理方式', 'model.eval() + torch.no_grad()，确定性推理；不训练、不调参、不搜索阈值', '阶段八_解释方法配置.json'),
    ('标准化参数', '复用问题二训练集拟合的冻结参数，不重新拟合', '阶段八_解释方法配置.json'),
    ('解释对象', '完整输入预测类别的概率 p(ŷ)；情感强度 r̂（分别定义贡献）', '阶段八_解释对象与基线说明.md'),
    ('模态级基线', '目标模态观测掩码整体置无效，输入置零', '阶段八_解释方法配置.json'),
    ('位置级遮蔽单元', f"文本单词元（步长1）；音频/视觉连续窗口 W={fc['window_length']}（步长1）", '阶段八_解释方法配置.json'),
    ('关键证据数', f"按 |Δcls| 降序取 Top-K，K={fc['top_k']}；忠实度对照 K=3", '阶段八_解释方法配置.json'),
    ('随机对照', f"同长度随机片段，重复 {fc['n_random_control']} 次取均值", '阶段八_解释方法配置.json'),
    ('输入扰动强度', 'σ ∈ {' + ', '.join(map(str, fc['noise_levels'])) + '}，仅加于已观测位置，各重复 3 次', '阶段八_解释方法配置.json'),
    ('窗口平移', '音频/视觉窗口整体平移 ±1 个桶位', '阶段八_解释稳定性分析.md'),
    ('解释随机种子', f"{fc['random_seed']}（仅用于随机对照与扰动抽样）", '阶段八_解释方法配置.json'),
    ('文本证据输出', '词元序号、词元、±3 词元上下文、是否功能词', '阶段八_解释方法配置.json'),
    ('音频/视觉证据输出', '附件2：桶位区间与相对位置（秒数不可回看）；附件4：重建秒数、帧号', '阶段八_解释方法配置.json / 阶段九_附件4预测与解释说明.md'),
], columns=['项目', '取值', '来源']), '表7-1_解释计算策略与参数设置.csv')

# 表7-2 验证集错误分析
c = rd('阶段八_验证集模态贡献.csv'); c['correct'] = c.y_true_class == c.pred_class
rows = []
for name, g in [('全部', c), ('预测正确', c[c.correct]), ('预测错误', c[~c.correct])] + [(f'{m}为主要模态', c[c['主要模态'] == m]) for m in ['文本', '音频', '视觉']]:
    rows.append((name, len(g), round(g.correct.mean(), 4), round(g.pred_prob_at_pred.mean(), 4),
                 round(g.text_Δcls_raw.mean(), 4), round(g.audio_Δcls_raw.mean(), 4), round(g.vision_Δcls_raw.mean(), 4)))
w(pd.DataFrame(rows, columns=['样本分组', '样本数', '准确率', '预测类别概率均值', '文本Δcls均值', '音频Δcls均值', '视觉Δcls均值']),
  '表7-2_验证集分组错误分析.csv')

# 表7-3 忠实度与稳定性
f = rd('阶段八_解释忠实度验证.csv'); rows = []
for K, g in f.groupby('K'):
    fl = g['预测翻转_topK'] == 1
    rows.append(dict(K=K, 有效样本=len(g), ΔP_TopK=round(g.ΔP_topK.mean(), 4), ΔP_随机=round(g.ΔP_random_mean.mean(), 4),
                     配对差=round(g['ΔP_差(重要-随机)'].mean(), 4), 配对差大于0比例=round((g['ΔP_差(重要-随机)'] > 0).mean(), 4),
                     Wilcoxon_p_材料值=cfg['validation_summary']['fidelity'][f'K={K}']['wilcoxon_p'],
                     Wilcoxon_p_CSV复算=float(f'{wilcoxon(g.ΔP_topK, g.ΔP_random_mean).pvalue:.3g}'),
                     翻转率_TopK=round(fl.mean(), 4), 翻转率_随机=round(g['预测翻转率_random'].mean(), 4),
                     翻转样本概率均值=round(g[fl].pred_prob_at_pred.mean(), 4), 未翻转样本概率均值=round(g[~fl].pred_prob_at_pred.mean(), 4),
                     强度绝对值变化_TopK=round(g['Δ|强度|_topK'].mean(), 4), 强度绝对值变化_随机=round(g['Δ|强度|_random'].mean(), 4),
                     配对差_文本组=round(g[g['解释模态'] == '文本']['ΔP_差(重要-随机)'].mean(), 4),
                     配对差_音频组=round(g[g['解释模态'] == '音频']['ΔP_差(重要-随机)'].mean(), 4),
                     配对差_视觉组=round(g[g['解释模态'] == '视觉']['ΔP_差(重要-随机)'].mean(), 4)))
w(pd.DataFrame(rows), '表7-3a_解释忠实度.csv')
s = rd('阶段八_解释稳定性验证.csv').drop(columns='sample_id').mean().round(4)
st = cfg['validation_summary']['stability']
rows = [(k, v, '阶段八_解释稳定性验证.csv') for k, v in s.items()]
rows += [(f'扰动σ{k}_排名Spearman', v, '阶段八_解释方法配置.json') for k, v in st['noise_rank_spearman'].items() if k != '0.5']
w(pd.DataFrame(rows, columns=['指标', '取值', '来源']), '表7-3b_解释稳定性.csv')

# 表7-4 验证集模态贡献统计
rows = []
for k, m in [('text', '文本'), ('audio', '音频'), ('vision', '视觉')]:
    x, y = c[f'{k}_Δcls_raw'], c[f'{k}_Δint_raw']
    rows.append((m, round(x.mean(), 4), round(x.std(ddof=0), 4), round(x.quantile(.1), 4), round(x.median(), 4), round(x.quantile(.9), 4),
                 round((x > 0).mean(), 4), round(y.mean(), 4), round((y > 0).mean(), 4), int((c['主要模态'] == m).sum())))
w(pd.DataFrame(rows, columns=['模态', 'Δcls均值', 'Δcls标准差(总体)', 'q10', '中位数', 'q90', 'Δcls>0比例', 'Δint均值', 'Δint>0比例', '主要模态样本数']),
  '表7-4_验证集三模态贡献统计.csv')

# 表7-5 附件4 20 条一览（四舍五入采用 ROUND_HALF_UP，与材料包 6 位小数原值的常规舍入一致）
from decimal import Decimal, ROUND_HALF_UP
hu = lambda s: s.map(lambda v: float(Decimal(repr(float(v))).quantize(Decimal('0.0001'), ROUND_HALF_UP)))
p = rd('q3_attachment4_predictions_explanations.csv', dtype={'sample_id': str})
P = p[['prob_neg', 'prob_neu', 'prob_pos']].values; srt = np.sort(P, 1)
POL = {'negative': '负向', 'neutral': '中性', 'positive': '正向'}
t5 = pd.DataFrame({'样本ID': p.sample_id, '时长/s': p.duration_s, '预测类别': p.pred_annotation.map(POL),
                   '负向概率': hu(p.prob_neg), '中性概率': hu(p.prob_neu), '正向概率': hu(p.prob_pos),
                   '最大概率': hu(pd.Series(P.max(1))), 'top1-top2': hu(pd.Series(srt[:, 2] - srt[:, 1])), '情感强度': hu(p.pred_intensity),
                   '文本Δcls': hu(p.text_contribution), '音频Δcls': hu(p.audio_contribution), '视觉Δcls': hu(p.vision_contribution),
                   '主要模态': p.dominant_modality, '回看结论': p['AI辅助回看判定'].replace({'人工回看支持': '支持'})})
w(t5, '表7-5_附件4预测与解释一览.csv')

# 表7-6 回看结论 × 预测类别
ct = pd.crosstab(t5['预测类别'], t5['回看结论']).reindex(index=['负向', '中性', '正向'], columns=['支持', '部分支持', '不支持', '无法确认']).fillna(0).astype(int)
ct['合计'] = ct.sum(axis=1)
ct['样本ID'] = [';'.join(f"{r['样本ID']}({r['回看结论']})" for _, r in t5[t5['预测类别'] == k].iterrows()) for k in ct.index]
w(ct.reset_index(), '表7-6_附件4回看结论与预测类别交叉.csv')

# 表7-3c 补充统计检验（正文 7.2.2、7.2.3、7.2.6 引用）
from scipy.stats import rankdata, pearsonr, mannwhitneyu
rows = []
for K, g in f.groupby('K'):
    d = g['ΔP_差(重要-随机)'].values; se = d.std(ddof=1) / np.sqrt(len(d))
    nz = d[d != 0]; r = rankdata(np.abs(nz)); rb = (r[nz > 0].sum() - r[nz < 0].sum()) / r.sum()
    pb = pearsonr(g.pred_prob_at_pred, g['预测翻转_topK'])
    rows += [(f'K={K} 配对差中位数', round(float(np.median(d)), 4)), (f'K={K} 配对差均值95%CI下限', round(d.mean() - 1.96 * se, 4)),
             (f'K={K} 配对差均值95%CI上限', round(d.mean() + 1.96 * se, 4)), (f'K={K} 配对秩二列相关rb', round(rb, 4)),
             (f'K={K} 完整输入概率与翻转的点二列相关r', round(pb.statistic, 4)), (f'K={K} 点二列相关p', float(f'{pb.pvalue:.3g}'))]
for col, lab in [('text_Δcls_raw', '文本Δcls'), ('pred_prob_at_pred', '预测类别概率')]:
    rows.append((f'正确vs错误 {lab} Mann-Whitney p', float(f'{mannwhitneyu(c[c.correct][col], c[~c.correct][col]).pvalue:.3g}')))
pr = pearsonr(P.max(1), p.text_contribution)
rows += [('附件4 最大概率与文本Δcls Pearson r', round(pr.statistic, 4)), ('附件4 Pearson p', float(f'{pr.pvalue:.3g}'))]
w(pd.DataFrame(rows, columns=['统计量', '取值']), '表7-3c_补充统计检验.csv')
