# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 23:50:33 2017

@author: 01550070
"""
import os
import win32com.client as win32

def outlook_mail (recipient, ZNO, roles, login,pswd ):
    outlook = win32.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)
    mail.To = recipient
    mail.CC = 'cc'
    mail.Subject = 'Вам предоставлен доступ к АС ЦХД по ' + ZNO
    mail.Body = """Добрый день!
В соответствии с %s Вам предоставлен доступ к \n
%s
Ваш логин: %s
Пароль: %s
\n\n
Для первоначального подключения смотрите инструкцию во вложении.
    """ %(ZNO, roles, login, pswd)
    mail.Attachments.Add(os.getcwd()+'\\'+'Инструкция по подключению и работе с БД Teradata(v5.2.11).docx')
    mail.Display(True)
    
    
def unlock_mail (recipient, ZNO, login, pswd ):
    outlook = win32.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)
    mail.To = recipient
    mail.CC = 'cc'
    mail.Subject = 'Сброс пароля по ' + ZNO
    mail.Body = """Добрый день! 
В соответствии с %s ваш пароль был сброшен на стандартный: 
Ваш логин: %s
Пароль: %s
\n\n
При первом подключении не забудьте сменить пароль на постоянный. Спасибо! 

    """ %(ZNO, login, pswd)
    mail.Display(True)