# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 13:15:21 2017

@author: 01550070
"""

def fib_gen(n):
    x = 0
    y = 1
    i = 0
    while i != n:
        yield x
        x,y = y, y + x
        i += 1


for i in fib_gen(100):
    print(i)