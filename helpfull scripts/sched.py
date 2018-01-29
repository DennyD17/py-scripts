# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 10:41:35 2017

@author: 01550070
"""

import schedule
import time

def job():
    print('I"m working')
    
schedule.every(15).minutes.do(job)
schedule.every().hour.at("10:15").do(job)
schedule.every().hour.at("10:30").do(job)
schedule.every().hour.at("10:45").do(job)
schedule.every().hour.at("10:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
