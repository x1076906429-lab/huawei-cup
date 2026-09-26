# -*- coding: utf-8 -*-
"""一键重建第七章全部图表与数据表：python fig7_all.py"""
import runpy, os
HERE = os.path.dirname(os.path.abspath(__file__))
for s in ['00_数据核验.py', 'tables7.py', 'fig7_1_method.py', 'fig7_2_3_validation.py', 'fig7_4_5_6_valset.py', 'fig7_7_8_att4.py']:
    print('==>', s); runpy.run_path(os.path.join(HERE, s), run_name='__main__')
