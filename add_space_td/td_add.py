# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 15:58:08 2017

@author: 01550070
"""
import teradata
import time
from datetime import date, datetime
import logging
from math import ceil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#VARS
logging.basicConfig(format=u'%(levelname)-8s[%(asctime)s] %(message)s', 
                    level=logging.DEBUG, filename=u'teradata_add_space.log')
udaExec = teradata.UdaExec ()
session = udaExec.connect("${dataSourceName}")
create_middle_db = 'CREATE DATABASE %s FROM "PRD3_GRP_DB" AS perm = %d;'
move_space_query = 'GIVE %s TO "%s";'
drop_middle_db = 'DROP DATABASE %s'
dict_for_mes = {}

# message_templates
no_shortage_template = "Space monitoting successfully finished. There wasn't shortage of space"
error_creating_temp_db = "Anything went wrong. Can't create temporary db %s from PRD3_GRP_DB with moving space"
error_mooving_space = "Can't move space from %s to %s."
error_dropping_temp_db = "Temporary DB %s wasn't dropped. Please drop it manualy"
accept_space_mooving = "Need to add %s to %s DB. Please accept space adding"     

# post adresses
to_td_admins = ['email']
to_ds = 'email'
to_test = ['email']
    

def send_mes (text, to, cc=None, smtp_host="localhost", from_mes='localhost'):
    text = MIMEText(text)
    msg = MIMEMultipart()
    msg['Subject'] = 'Free space TD monitoring'
    msg['From'] = from_mes
    msg['To'] = ', '.join(to)
    if cc:
        msg['Cc'] = ','.join(cc)
    msg.attach(text)
    server = smtplib.SMTP(smtp_host)
    server.sendmail(from_mes, to, msg.as_string())
    logging.info("message was sent")
    server.quit()

    
def delete_temp_db(db_name):
    try:
        logging.info("Trying to delete temporary db")
        session.execute(drop_middle_db %db_name, queryTimeout=180)
    except Exception as e:
        logging.critical("can't drop temporary database %s" %db_name)
        logging.critical(str(e))
        send_mes(error_dropping_temp_db %db_name, to_td_admins)
        return False
    else:
        logging.info("Temporary database %s was droped" %db_name)
        return True


def move_space(db_name, space_to_add_gb):
    space_to_add_b = 1024 * 1024 * 1024 * space_to_add_gb
    middle_db_name = 'TDAdmin' + str(date.today().strftime('%d%b%Y')) 
    try:
        logging.info("Trying to create temporary db")
        session.execute(create_middle_db %(middle_db_name, space_to_add_b))
    except Exception as e:
        logging.critical("Can't create db %s from PRD3_GRP_DB with moving space" %middle_db_name)
        logging.critical(str(e))
        exit 
    else:
        delay = 0
        while 1 == 1:
            try:
                session.execute(move_space_query %(middle_db_name, db_name), queryTimeout=300)
            except Exception as e:
                logging.warning(str(e))
                logging.debug('Starting to sleep...zzz')
                time.sleep(150 + delay)
                delay += 150
                if delay > 599:
                    delete_temp_db(middle_db_name)
                    return "Cant move space to %s" %db_name
                pass
            else:
                logging.info('space for %s has been moved' %db_name)
                break
        delete_temp_db(middle_db_name)
        return db_name + " need to add " + str(space_to_add_gb) + " - SUCCESS"
    
       
        

def space_check():
    try:
        result = session.execute(file='space_analyze_script.sql', queryTimeout=900)
    except Exception as e:
        logging.info(str(e))
        logging.warning("The query for space monitoryng is executing longer then timeout setting. Sleep for 5 minutes")
        time.sleep(1800)
        space_check()
    else:
        if result.rowcount > 0:
            for row in result:
                dict_for_mes[row[0]] = ceil(float(row[1]))
                logging.info(row[0] + ' - ' + str(dict_for_mes[row[0]]) + 'GB')
            adding_results = [move_space(key, value) if value < 1500 else send_mes(accept_space_mooving % (str(value), key), to_td_admins) for key, value in dict_for_mes.items()]
            adding_results = [x for x in adding_results if x is not None]
            session.close()
            logging.info(adding_results)
            if adding_results != []:
                send_mes('\n'.join(adding_results), to_td_admins)
        else:
            logging.info("There wasn't shortage of space")
            send_mes(no_shortage_template, to_td_admins)
            session.close()

                
space_check()