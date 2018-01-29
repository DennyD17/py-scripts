# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 11:33:33 2017

@author: 01550070
"""
import random

a = [random.randint(0, 5000) for i in range(0,3)]
print(a)

def quick_sort(l):
    if l == []:
        return []
    else:        
        less_supp = [item for item in l if item < l[0]]
        bigger_supp = [item for item in l if item >= l[0]]
        return quick_sort(less_supp) + quick_sort(bigger_supp)
    
print(quick_sort(a))
