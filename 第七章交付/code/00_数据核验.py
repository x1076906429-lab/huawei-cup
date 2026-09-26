# -*- coding: utf-8 -*-
"""第七章数值核验：从材料包原始 CSV/JSON 重新计算正文将使用的全部统计量，输出 data/verified_numbers.json。
标准差口径：附件4 统计与材料包一致，采用总体标准差（ddof=0）；验证集同时给出 ddof=1。"""
import json, os
import numpy as np, pandas as pd
from scipy.stats import wilcoxon

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, '第七章交付', 'data', 'verified_numbers.json')
rd = lambda f, **k: pd.read_csv(os.path.join(ROOT, f), encoding='utf-8-sig', **k)
r4 = lambda x: float(round(float(x), 4))
V = {}

# ---- 验证集模态贡献 ----
c = rd('阶段八_验证集模态贡献.csv')
c['correct'] = c.y_true_class == c.pred_class
V['val'] = dict(n=len(c), n_unique=int(c.sample_id.nunique()), acc=r4(c.correct.mean()),
                pred_prob_mean=r4(c.pred_prob_at_pred.mean()),
                confusion=pd.crosstab(c.y_true_class, c.pred_class).values.tolist(),
                dominant=c['主要模态'].value_counts().to_dict())
for m in ['text', 'audio', 'vision']:
    x, y = c[f'{m}_Δcls_raw'], c[f'{m}_Δint_raw']
    V['val'][m] = dict(cls_mean=r4(x.mean()), cls_sd_ddof0=r4(x.std(ddof=0)), cls_sd_ddof1=r4(x.std()),
                       q10=r4(x.quantile(.1)), median=r4(x.median()), q90=r4(x.quantile(.9)),
                       cls_pos=r4((x > 0).mean()), int_mean=r4(y.mean()), int_sd=r4(y.std(ddof=0)),
                       int_pos=r4((y > 0).mean()))
g = c.groupby('correct')
V['val']['by_correct'] = {str(k): dict(n=int(len(v)), prob=r4(v.pred_prob_at_pred.mean()),
                          text=r4(v.text_Δcls_raw.mean()), audio=r4(v.audio_Δcls_raw.mean()),
                          vision=r4(v.vision_Δcls_raw.mean())) for k, v in g}
V['val']['by_dominant'] = {k: dict(n=int(len(v)), prob=r4(v.pred_prob_at_pred.mean()), acc=r4(v.correct.mean()),
                           text=r4(v.text_Δcls_raw.mean())) for k, v in c.groupby('主要模态')}

# ---- 忠实度 ----
f = rd('阶段八_解释忠实度验证.csv')
V['fidelity'] = {}
for K, gk in f.groupby('K'):
    d = gk['ΔP_差(重要-随机)']; fl = gk['预测翻转_topK'] == 1
    V['fidelity'][int(K)] = dict(n=len(gk), dP_top=r4(gk.ΔP_topK.mean()), dP_rand=r4(gk.ΔP_random_mean.mean()),
        diff=r4(d.mean()), diff_pos=r4((d > 0).mean()),
        wilcoxon_p_recomputed=float(wilcoxon(gk.ΔP_topK, gk.ΔP_random_mean).pvalue),
        flip_top_n=int(fl.sum()), flip_top=r4(fl.mean()), flip_rand_n=r4(gk['预测翻转率_random'].sum()),
        flip_rand=r4(gk['预测翻转率_random'].mean()),
        prob_flip=r4(gk[fl].pred_prob_at_pred.mean()), prob_noflip=r4(gk[~fl].pred_prob_at_pred.mean()),
        corr_prob_flip=r4(np.corrcoef(gk.pred_prob_at_pred, fl)[0, 1]),
        dInt_top=r4(gk['Δ|强度|_topK'].mean()), dInt_rand=r4(gk['Δ|强度|_random'].mean()),
        by_modality={m: dict(n=int(len(v)), diff=r4(v['ΔP_差(重要-随机)'].mean())) for m, v in gk.groupby('解释模态')})

# ---- 稳定性 ----
s = rd('阶段八_解释稳定性验证.csv').drop(columns='sample_id')
V['stability'] = {k: r4(v) for k, v in s.mean().items()}
V['stability_constant_columns'] = [k for k, n in s.nunique().items() if n == 1]
cfg = json.load(open(os.path.join(ROOT, '阶段八_解释方法配置.json'), encoding='utf-8'))
V['stability_json'] = cfg['validation_summary']['stability']

# ---- 稀疏性 / 关键证据 ----
sp = rd('阶段八_解释稀疏性与可回看性.csv')
V['sparsity'] = {k: float(round(v, 2)) for k, v in sp[['文本_可评估词元数', '文本_保留关键词元数', '音频_可评估窗口数',
                 '音频_保留关键窗口数', '视觉_可评估窗口数', '视觉_保留关键窗口数']].mean().items()}
V['dispersed'] = {m: int((sp[m] == '是').sum()) for m in ['文本_关键词元是否分散', '音频_关键窗口是否分散', '视觉_关键窗口是否分散']}
e = rd('阶段八_验证集关键证据.csv')
t = e[e.modality == 'text']
V['val_evidence'] = dict(rows=len(e), by_modality=e.modality.value_counts().to_dict(),
    direction=pd.crosstab(e.modality, e['方向']).to_dict(), abs_mean=r4(e['Δcls'].abs().mean()),
    abs_max=r4(e['Δcls'].abs().max()), stop_top5=r4((t['是否功能词'] == '是').mean()),
    stop_rank1=r4((t[t['rank'] == 1]['是否功能词'] == '是').mean()))

# ---- 附件4 ----
p = rd('q3_attachment4_predictions_explanations.csv', dtype={'sample_id': str})
P = p[['prob_neg', 'prob_neu', 'prob_pos']].values; mx = P.max(1); srt = np.sort(P, 1)
V['att4'] = dict(n=len(p), dist=p.pred_annotation.value_counts().to_dict(),
    argmax_consistent=bool((P.argmax(1) == p.pred_class).all()), rowsum_maxdev=float(abs(P.sum(1) - 1).max()),
    maxp_mean=r4(mx.mean()), maxp_median=r4(np.median(mx)), maxp_sd_ddof0=r4(mx.std()), maxp_sd_ddof1=r4(mx.std(ddof=1)),
    maxp_min=r4(mx.min()), maxp_max=r4(mx.max()), n_high=int((mx > .9).sum()), low_ids=list(p.sample_id[mx < .5]),
    int_mean=r4(p.pred_intensity.mean()), int_median=r4(p.pred_intensity.median()),
    int_sd_ddof0=r4(p.pred_intensity.std(ddof=0)), int_sd_ddof1=r4(p.pred_intensity.std()),
    int_min=r4(p.pred_intensity.min()), int_max=r4(p.pred_intensity.max()),
    dominant=p.dominant_modality.value_counts().to_dict(),
    review=pd.crosstab(p.pred_annotation, p['AI辅助回看判定']).to_dict(),
    class_intensity_sign_mismatch=list(p.sample_id[((p.pred_annotation == 'positive') & (p.pred_intensity < 0)) |
                                                     ((p.pred_annotation == 'negative') & (p.pred_intensity > 0))]),
    per_sample={r.sample_id: dict(pred=r.pred_annotation, maxp=r4(m_), gap=r4(sr[2] - sr[1]), intensity=r4(r.pred_intensity),
                text=r4(r.text_contribution), audio=r4(r.audio_contribution), vision=r4(r.vision_contribution),
                dominant=r.dominant_modality, review=rv)
                for r, m_, sr, rv in zip(p.itertuples(), mx, srt, p['AI辅助回看判定'])})
for m in ['text', 'audio', 'vision']:
    V['att4'][m] = dict(cls_mean=r4(p[f'{m}_contribution'].mean()), cls_pos=r4((p[f'{m}_contribution'] > 0).mean()))
ev = rd('阶段九_附件4关键证据明细.csv', dtype={'sample_id': str})
V['att4_evidence'] = dict(rows=len(ev), by_modality=ev.modality.value_counts().to_dict(),
    text_stop=int((ev[ev.modality == 'text'].is_stopword == '是').sum()))
V['keyframes_present'] = sorted(os.listdir(os.path.join(ROOT, '关键帧')))
V['keyframes_png_count'] = sum(len(fs) for _, _, fs in os.walk(os.path.join(ROOT, '关键帧')))

json.dump(V, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print('written', OUT)
