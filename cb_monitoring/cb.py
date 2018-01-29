# -*- coding: utf-8 -*-

import urllib.request as urllib2
import smtplib
from email.mime.text import MIMEText

from bs4 import BeautifulSoup


url = 'https://www.cbr.ru/'
resp = urllib2.urlopen(url)
list_of_td_values = []
ind = 'not found'
soup = BeautifulSoup(resp.read(), 'html.parser', from_encoding='utf-8')
for td in soup.find_all('td'):
    list_of_td_values.append(td.text)
for val in list_of_td_values:
    if 'Ключевая' in val:
        words = val
        ind = list_of_td_values.index(val)
f = open('old_state.txt', 'r')
old_state = f.read()
f.close()

if old_state != list_of_td_values[ind+1]:
        msg = list_of_td_values[ind] + '  ' + list_of_td_values[ind+1] + '\nСтавка изменилась. \nСтарая ставка = ' + \
              old_state
        f = open('old_state.txt', 'w')
        f.write(list_of_td_values[ind+1])
        f.close()
else:
    msg = list_of_td_values[ind] + '   ' + list_of_td_values[ind+1] + '\nСтавка не изменилась. '
msg = MIMEText(msg)
print(msg)

fromaddr = ''
toaddrs = ['']
username = ''
password = ''
server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()
server.login(username, password)
server.sendmail(fromaddr, toaddrs, msg.as_string())
server.quit()

