# 第七章交付物

| 序号 | 交付内容 | 文件 |
|---|---|---|
| 1 | 完整第七章正文（按指定目录 7.1.1～7.3） | `问题三第七章正文.docx`（Word，公式可编辑）；源稿 `问题三第七章正文.md`；重新生成：`python code/build_docx.py` |
| 2 | 图7-1～图7-8（PNG 300 dpi / 可编辑 SVG / PDF）及绘图代码 | `figures/`；`code/fig7_*.py`，一键重建：`cd code && python fig7_all.py` |
| 3 | 正文使用的数据表 | `data/表7-1～表7-6*.csv`；复算值 `data/verified_numbers.json` |
| 4 | 结论—数据来源—文件名对应表 | `02_结论数据来源对应表.md` |
| 5 | 附件材料清单 | `03_附件材料清单.md` |
| 6 | 数据缺失、冲突与无法验证内容说明 | `01_数据缺失冲突与修改事项.md` |
| 7 | 最终核验记录 | `04_最终核验记录.md`；自动核验 `code/99_正文核验.py` |
| — | 首轮核查报告（写作前） | `00_首轮核查报告.md` |

依赖：Python 3、pandas、numpy、scipy、matplotlib。所有代码只读取仓库根目录的材料包文件，不修改原始数据。

终稿换字体：修改 `code/fig7_common.py` 中的 `FONT_CN = ['SimSun']`、`FONT_EN = ['Times New Roman']` 后重新运行 `fig7_all.py`。
