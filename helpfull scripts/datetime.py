# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 15:52:28 2017

@author: 01550070
"""

from datetime import  datetime, timedelta

print((datetime.now() - timedelta(minutes=15)).strftime('%Y-%m-%d %X'))