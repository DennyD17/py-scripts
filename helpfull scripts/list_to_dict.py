# -*- coding: utf-8 -*-
"""
Created on Fri Oct  6 13:26:00 2017

@author: 01550070
"""

keys = ['awd','dwa','wad', 'aw']
items = ['dd', 'ddd', 'aa']
items1 = ['z', 'r', 'q', 'f', 'g']


if len(items) < len (keys):
    [items.append(None) for i in range(len(items), len(keys))]
print ({ key: value for key, value in zip(set(keys),items)})
print ({ key: value for key, value in zip(set(keys),items1)})
