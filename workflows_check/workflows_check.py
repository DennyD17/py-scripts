#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
import cx_Oracle
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from settings import post_adress, test


#PARAMS & VARS

#logging
logging.basicConfig(format=u'%(levelname)-8s[%(asctime)s] %(message)s', 
                    level=logging.DEBUG, filename=u'wf_monitoring.log')

#TD
#udaExec = teradata.UdaExec()
#session = udaExec.connect("${dataSourceName}")

#ORACLE
conn_str = ''
connection = cx_Oracle.connect(conn_str)
cursor = connection.cursor()

#SENDING MESSAGES
mes_template = '!Warning! Workflow %s didnt %s at %s at Vol %s'
to_ds = ''
to_test = [post_adress]
to_loading_admins = ['']



def send_mes (text, to, cc=None, smtp_host="localhost", from_mes=''):
    text = MIMEText(text)
    msg = MIMEMultipart()
    msg['Subject'] = 'Workflows checking'
    msg['From'] = from_mes
    msg['To'] = ', '.join(to)
    if cc:
        msg['Cc'] = ','.join(cc)
    msg.attach(text)
    server = smtplib.SMTP(smtp_host)
    server.sendmail(from_mes, to, msg.as_string())
    logging.info("message was sent")
    server.quit()


def get_params_from_file():
    params = []
    with open ('wfs_to_check.data', 'r') as f:
        for line in f.readlines():
            params.append(line.split())
    return params
    

def is_started(workflow, instance, part):
    filename = 'wf_1.sql' if part == "1" else 'wf_0.sql'
    with open (filename, 'r') as f:
        result = cursor.execute(f.read() %(workflow, instance)).fetchone()
        logging.info(result)
    return True if result else False
    
    
def is_finished(workflow, instance, part):
    filename = 'wf_1.sql' if part == "1" else 'wf_0.sql'
    with open (filename, 'r') as f:
        result = cursor.execute(f.read() %(workflow, instance)).fetchone()
        logging.info(result)
    return True if result and result[3] <= 2 else False
    

def checking():
    params = get_params_from_file()
    for wf_params in params:
        logging.debug('Trying to search for '+ str(wf_params))
        if wf_params[2] == datetime.strftime(datetime.now(), '%H:%M'):
            if not is_started(wf_params[0], wf_params[1], wf_params[4]):
                mes = mes_template %((wf_params[0] + '_' + wf_params[1]), 'start', wf_params[2], wf_params[4])
                logging.error(mes)
                send_mes(mes, to_loading_admins)
        if wf_params[3] == datetime.strftime(datetime.now(), '%H:%M'):
            if not is_finished(wf_params[0], wf_params[1], wf_params[4]):
                mes = mes_template %((wf_params[0] + '_' + wf_params[1]), 'finish', wf_params[3], wf_params[4])
                logging.error(mes)
                send_mes(mes, to_loading_admins)


if test:
    to_ds = post_adress
    to_loading_admins = post_adress

checking()	          