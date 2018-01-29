# -*- coding: utf-8 -*-

try:
	import urllib.request as urllib2
	import http.cookiejar as cookielib
	import urllib.parse as parse
except Exception:
	import urllib2
	import cookielib
	from urllib import urlencode as parse
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import logging
import ssl
import argparse

from settings import domain_login, domain_pwd, test, post_adress


logging.basicConfig(format=u'%(levelname)-8s[%(asctime)s] %(message)s', level=logging.DEBUG, filename=u'sas_monitoring.log')


class System ():
    systems = []
    def __init__(self, name, url, login_url, selector, is_tokken, login_form_data, login_page_succses_text):
        self.name = name
        self.url = url
        self.login_url = login_url
        self.selector = selector
        self.is_tokken = is_tokken
        self.login_form_data = login_form_data
        self.login_page_succses_text = login_page_succses_text
        self.systems.append(self)
		
    def system_check(self):
        logging.info('Checking %s :' %self.name)
        cookie = cookielib.CookieJar()
        ctx = ssl._create_unverified_context()
        req = urllib2.build_opener(urllib2.HTTPSHandler(context=ctx), urllib2.HTTPCookieProcessor(cookie))
        req.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36')]
        if self.is_tokken == True:
            try:
                soup = BeautifulSoup(req.open(self.login_url).read(), 'html.parser', from_encoding='utf-8')
            except Exception as e:
                logging.error(str(e))
                return '%s: ERROR.main page is unavailible\n' %self.name
            else:
                tokken = str(soup.find('input', {'name': 'lt'}).get('value'))
                exe = str(soup.find('input', {'name': 'execution'}).get('value'))
                self.login_form_data['lt'] = tokken
                self.login_form_data['execution'] = exe
        try:
            resp = req.open(self.login_url, parse(self.login_form_data).encode())
        except Exception as e:
            logging.error(str(e))
            return "%s: ERROR.Exception while trying to login\n" %self.name
        else:
            if self.login_page_succses_text in str(resp.read()):
                logging.info("%s.Successfull login" %self.name)
                try:
                    start = time.time()
                    resp = req.open(self.url)
                except Exception as e:
                    logging.error(str(e))
                    return "%s: ERROR.Exception while trying open main page\n" %self.name
                else:
                    page_code = str(resp.read())
                    if self.selector in page_code:
                        end = time.time()
                        logging.info('%s: OK.Main page is availible. Response time = %s\n' % (self.name, str(end - start)[0:4]))
                        return '%s: OK.Main page is availible. Response time = %s\n' % (self.name, str(end - start)[0:4])
                    else:
                        logging.error("can't open main page\n")
                        with open('%s_page_code_%s.txt' % (self.name, str(datetime.now())), 'w') as f:
                           f.write(page_code)
                        return '%s: ERROR.main page is unavailible' %self.name
            else:
                logging.error("%s: ERROR while trying to login\n" %self.name)
                return "%s: ERROR while trying to login" %self.name
	
	def __repr__(self):
		return self.name
                        
                
suor = System('SUOR PROM', 
              '',
              '',
              'toolBar', False, 
              {'domain':'', 'username':domain_login, 'password': domain_pwd, 'login-form-type': ''}, 
              'Your login was successful')


erm_prom = System('ERM PROM', 
                 '',
                 '',
                 'aggregation-loading-results', True,
                 {'username': '', 'password': '', '':'', '': '', '': ''}, 
                 'aggregation-loading-results')

MM3 = System( 'MM3', 
              '',
              '',
              'nav-stacked', False, 
              {'domain':'', 'username':, 'password': , 'login-form-type': 'pwd'}, 
              'Your login was successful')



to_mm3 = ['email']
to_sas = ['email']
to_ds = ['email']
to_sms = ['mail']
to_test = [post_adress]
    

def send_mes (text, to, cc=None, smtp_host="localhost", from_mes='localhost'):
    text = MIMEText(text)
    msg = MIMEMultipart()
    msg['Subject'] = 'SAS check'
    msg['From'] = from_mes
    msg['To'] = ','.join(to)
    if cc:
        msg['Cc'] = ','.join(cc)
    msg.attach(text)
    server = smtplib.SMTP(smtp_host)
    if smtp_host != "localhost":
		smtp_user = post_adress
		login = domain_login
		smtp_pass = domain_pwd
		server.ehlo()
		server.starttls()
		server.login(login, smtp_pass)
    server.sendmail(from_mes, to, msg.as_string())
    server.quit()


def monitoring():
    with open('systems2check.dat', 'r') as f:
        systems_to_check = [system for system in f.read().splitlines()]
    results = [system.system_check() for system in System.systems if system.name in systems_to_check]
    for one in results:
        if 'ERROR' in one and 'MM3' not in one:
            send_mes(one, to_sms, to_sas, smtp_host="Outlook", from_mes=post_adress)
            send_mes(one, to_sas)
        elif 'ERROR' in one and 'MM3' in one:
            send_mes(one, to_sms, to_mm3, smtp_host="Outlook", from_mes=post_adress)
            send_mes(one, to_mm3)
    if datetime.strftime(datetime.now(), '%H:%M') == '04:00' or datetime.strftime(datetime.now(), '%H:%M') == '00:00':
        send_mes('\n'.join(results), to_mm3 + to_sas)
		

		
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", "--test", action="store_true", help="test mode")
    parser.add_argument("-email", "--email", action="store", type=str, help="email to send check results. default - DS OSPPR email", default=''.join(to_ds))
    args = parser.parse_args()
    test_email = [args.email]
    if args.test:
        with open('systems2check.dat', 'r') as f:
            systems_to_check = [system for system in f.read().splitlines()]
        results = [system.system_check() for system in System.systems if system.name in systems_to_check]
        send_mes('\n'.join(results), test_email)
    else:
        monitoring()
