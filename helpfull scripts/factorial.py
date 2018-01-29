# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 11:43:40 2017

@author: 01550070
"""
import time


def time_deco(func):
    def timer (*args, **kwargs):
        start_time = time.time()
        return func(*args, **kwargs), (time.time() - start_time)
    return timer


@time_deco
def factorial(n):
    fact = 1
    for i in range(1, n+1):
        fact *= i
    return fact

   
def factorial_rec(n):
    return 1 if n-1 == 0 else factorial_rec(n-1) * n
        

facto = lambda x: 1 if x-1 == 0 else x * facto(x-1)




print(factorial(20))
print(factorial_rec(10))
