# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 13:20:17 2017

@author: 01550070
"""

a = [
    '3_av.txt',
    '1_vv.txt',
    '1_awd.txt',
    '2_aa.txt',
    '3_zav.txt',
    '3_b.txt',
    '13_b.txt',
    
]


print(sorted(a))
print(sorted(a, key=lambda item: (int(item.split('_')[0]), item.split('_')[1].lower())))


