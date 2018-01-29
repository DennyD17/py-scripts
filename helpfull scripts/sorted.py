# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 17:30:47 2017

@author: 01550070
"""

a = [1,2,3,4,5,3,4,5,6,7,3,2,3,4,5,6,7,5,4,4]
d = {}

for item in a:
    try:
        d[item] += 1
    except KeyError:
        d[item] = 1
    else:
        continue
    
print(sorted(d.items(), key=lambda item: item[1], reverse=True))
print(sorted(d.items(), key=lambda item: (item[1], item[0]), reverse=True))
