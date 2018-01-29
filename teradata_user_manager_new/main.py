# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 11:26:51 2017

@author: 01550070
"""

import cx_Oracle
from bs4 import BeautifulSoup
import re
import pyodbc
import teradata
import logging
import socket
import pickle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from collections import OrderedDict

from queries import *
from settings import *
from roles_list import roles_list


class User(object):
    def __init__(self, znr_info, adressbook_info):
        """
        Contain fields:
        self.tab_number
        self.first_name
        self.surname
        self.patronymic
        self.user_alpha_email
        self.user_sigma_email
        self.user_omega_email
        self.login
        self.roles_to_add
        self.tab_number_from_adresbook
        self.znr_number
        self.system_type
        self.tb_code
        """
        {setattr(self, key, value) for key, value in znr_info.items()}
        {setattr(self, key, value) for key, value in adressbook_info.items()}
        self.login = self.translit(self.surname + '-' + self.first_name[0] + self.patronymic[0])
        # Если из телефонного справочника пришел код тербанка, то добавляем его к логину
        if self.tb_code:
            self.login = self.tb_code + '-' + self.login
        # Если забирая информацию из телефонного справочника удалось забрать табельный номер,
        # то этот табельный номер считаем действительным
        self.tab_number = self.tab_number_from_adresbook if self.tab_number_from_adresbook else self.tab_number
        # Если из система определена как ПРОМ, то используем конфиг для подключения к ПРОМ, иначе к ПСИ
        td_config_file = 'udaexec.ini' if self.system_type == 'prom' else 'uratd_exec.ini'
        udaexec = teradata.UdaExec(appConfigFile=td_config_file)
        self.session = udaexec.connect("${dataSourceName}")
        self.is_created = False
        self.added_roles = []

    @classmethod
    def create_valid_user(cls, znr):
        # Перед вызовом конструктора проверям, удалось ли получить информацию в СМ и телефонном справочнике
        creating_object_dict = OrderedDict()
        znr_dict = cls.get_znr_info(znr)
        if znr_dict['result'] != 'OK':
            return None, znr_dict
        else:
            creating_object_dict['getting info from SM'] = 'OK'
            adressbook_info = cls.get_user_info_from_adressbook(znr_dict['surname'] + znr_dict['first_name'] +
                                                                znr_dict['patronymic'], znr_dict['tab_number'])
            if adressbook_info['result'] != 'OK':
                return None, adressbook_info
            else:
                creating_object_dict['getting info from Adressbook'] = 'OK'
                return cls(znr_dict, adressbook_info), creating_object_dict

    def get_fullname(self):
        return self.surname + ' ' + self.first_name + ' ' + self.patronymic

    def existing_user(self):
        """
        Проверяем, существует ли юзер в ТД
        """
        logging.info('Trying to find user %s in Teradata' % self.login)
        # Пробуем найти по сформированному логину
        if self.session.execute(td_select_users_by_login % self.login).rowcount == 1:
            logging.info('User %s was found in Teradata' % self.login)
            return True
        # Если найти не удалось, пробуем найти по почте альфа, если она имеется
        elif self.user_alpha_email and self.session.execute(td_select_user_by_alpha % self.user_alpha_email).rowcount == 1:
            self.login = self.session.execute(td_select_user_by_alpha % self.user_alpha_email).fetchone()[0]
            logging.info('User %s was found in Teradata by alpha email' % self.login)
            return True
        # Если найти не удалось, пробуем найти по почте omega, если она имеется
        elif self.user_omega_email and self.session.execute(td_select_user_by_alpha % self.user_omega_email).rowcount == 1:
            self.login = self.session.execute(td_select_user_by_alpha % self.user_omega_email).fetchone()[0]
            logging.info('User %s was found in Teradata by omega email' % self.login)
            return True
        # Если найти не удалось, пробуем найти по почте сигма, если она имеется
        elif self.user_sigma_email and self.session.execute(td_select_user_by_sigma % self.user_sigma_email ).rowcount == 1:
            self.login = self.session.execute(td_select_user_by_sigma % self.user_sigma_email).fetchone()[0]
            logging.info('User %s was found in Teradata by sigma email' % self.login)
            return True
        else:
            logging.info('Cant find user %s in Teradata' % self.login)
            return False
            
    def grant_roles(self):
        """
        Выдаем роли
        """
        # Словарь для передачи в словарь для ответа клиенту
        adding_roles_dict = OrderedDict()
        for role in self.roles_to_add:
            # Пытаемся найти роль в словаре соответствия технического наименования ролей наименованию ролей в СМ
            try:
                role_td = roles_list[role]
            except KeyError:
                logging.error("Cant find role '%s' in roles_list.py" % role)
                adding_roles_dict['adding role %s' % role] = "Cant find role in roles_list.py"
            else:
                # Если роль удалось найти пробуем выдать ее
                try:
                    self.session.execute(td_grant_roles_query % (self.login, role_td))
                except Exception as e:
                    logging.error("Cant grant role %s" % role)
                    logging.error(str(e))
                    adding_roles_dict['adding role %s' % role] = "Cant grant role "
                else:
                    self.added_roles.append(role)
                    adding_roles_dict['adding role %s' % role] = "role was granted"
        return adding_roles_dict
        
    def create_user(self):
        """
        Создание пользователя в Терадате.
        Заключается в запуске процедуры с переданными параметрами.
        """
        # Словарь для передачи в словарь для ответа клиенту
        creating_user_dict = OrderedDict()
        logging.info('Trying to create user %s' % self.login)
        try:
            self.session.execute(td_create_user % (self.login, self.tab_number,
                                                   self.login, self.user_alpha_email,
                                                   self.user_sigma_email, self.surname,
                                                   self.first_name, self.patronymic))
        except Exception as e:
            logging.critical('Cant create user %s on Teradata' % self.login)
            logging.critical(str(e))
            creating_user_dict['creating_user_in_td'] = 'Cant create user %s on Teradata.' % self.login
            creating_user_dict['creating_user_fail_reason'] = str(e)
            creating_user_dict['created'] = False
            return creating_user_dict
        else:
            creating_user_dict['creating_user_in_td'] = 'User %s was successfully created' % self.login
            creating_user_dict['created'] = True
            self.is_created = True
            return creating_user_dict
            
    def __repr__(self):
        return "Сотрудник %s, запрашивающий доступ к %s, предполагаемый логин %s, почта Альфа - %s" %\
                (self.get_fullname(), self.system_type, self.login, self.user_alpha_email)

    @staticmethod
    def translit(str_to_translit):
        """
        Метод, возвращающий полученную строку на латинице
        """
        translited_str = ''
        str_to_translit = str_to_translit.lower()
        alphabet = {
            'а': 'a',
            'б': 'b',
            'в': 'v',
            'г': 'g',
            'д': 'd',
            'е': 'e',
            'ж': 'j',
            'з': 'z',
            'и': 'i',
            'й': 'i',
            'к': 'k',
            'л': 'l',
            'м': 'm',
            'н': 'n',
            'о': 'o',
            'п': 'p',
            'р': 'r',
            'с': 's',
            'т': 't',
            'у': 'u',
            'ф': 'f',
            'х': 'h',
            'ц': 'c',
            'ч': 'ch',
            'ш': 'sh',
            'щ': 'shc',
            'ъ': '',
            'ы': 'i',
            'ь': '',
            'э': 'e',
            'ю': 'yu',
            'я': 'ya',
        }
        for symbol in str_to_translit:
            try:
                translited_str += alphabet[symbol]
            except KeyError:
                translited_str += symbol
        return translited_str

    @staticmethod
    def get_user_info_from_adressbook(fio, tab_num):
        """

        :param fio: Фамилия Имя Отчество пользователя не разделенные пробелами
        :param tab_num: табельный номер, полученный из СМ
        :return: почта Альфа, почта Сигма, табельный номер из справочника, код тербанка
        """
        terbank_codes = {
            'ЮЗБ': 'UZB',
            'ПБ': 'PVB',
            'СРБ': 'SRB',
            'УБ': 'URB',
            'ВВБ': 'VVB',
            'СИБ': 'SIB',
            'СЗБ': 'SZB',
            'ЦЧБ': 'CCB',
            'ЗСБ': 'ZSB',
            'ЗУБ': 'ZUB',
            'СБТ': 'SBT',
            'ББ': 'BB',
            'ДВБ': 'DVB',
            'СЕВ': 'SEV',
        }
        # Пытаемся соединиться с БД тел.справочника
        logging.info('Trying connect to adressbook DB')
        try:
            connection = pyodbc.connect(adresbook_connection_string)
        except pyodbc.DatabaseError:
            logging.critical('Cant connect to adressbook database')
            return OrderedDict({'result': 'fail', 'adressbook_fail_reason': 'Cant connect to adressbook database'})
        logging.info('Successfully connected to adressbook DB')
        cursor = connection.cursor()
        logging.info('Trying to get information from SM by user fio')
        rows_by_fio = cursor.execute(adressbook_find_user_by_fio % fio).fetchall()
        # Если запрос в телефонный справочник по фио вернул один результат, то считаем его истинным
        if len(rows_by_fio) == 1:
            logging.info('User was found in adressbook by fio')
            row = rows_by_fio[0]
            logging.info(row)
        # Иначе пробуем найти пользователя по табельному номеру из СМ
        else:
            logging.info('Trying to get information from SM by user tab number')
            rows_by_tab_num = cursor.execute(adressbook_find_user_by_tab_number % tab_num).fetchall()
            if len(rows_by_tab_num) == 1:
                logging.info('User was found in adressbook by tab number')
                row = rows_by_tab_num[0]
                logging.info(row)
            else:
                row = None
        if row:
            # Проверяем, относится ли пользователь к какому-либо тер.банку
            try:
                tb_code = terbank_codes[row[2]]
            except KeyError:
                tb_code = None
            return {'result': 'OK', 'user_alpha_email': row[0], 'user_sigma_email': row[1],
                   'tab_number_from_adresbook': row[3], 'tb_code': tb_code, 'user_omega_email': row[4]}
        else:
            logging.critical('Cant find info about user %s (%s) in adresbook' % (fio, tab_num))
            return OrderedDict({'result': 'fail', 'adressbook_fail_reason': 'Cant find info about user %s (%s) in adresbook' % (fio, tab_num)})

    @staticmethod
    def get_znr_info(znr):
        """
        Получение информации из БД СМ
        :param znr: Номер ЗНР в формате "ЗНР12345678"
        :return: Фамилия, имя , отчество, список запрашиваемых ролей, табельный номер, тип системы (ПРОМ или ПСИ)
        """
        conn_str = sm_connection_string
        logging.info("Trying connect to SM DB")
        try:
            connection = cx_Oracle.connect(conn_str)
        except cx_Oracle.DatabaseError as e:
            logging.critical("Can't connect to SM database, check settings.py")
            logging.info(str(e))
            return OrderedDict({'result': 'fail', 'sm_fail_reason': "Can't connect to SM database, check settings.py"})
        else:
            logging.info("Successfully connected to SM database")
            cursor = connection.cursor()
        logging.info('Trying to find and parse information about %s at SM' % znr)
        try:
            options_xml = cursor.execute(sm_get_znr_oprions_query % znr).fetchone()[0]
        except TypeError:
            logging.critical('Cant find %s in SM database' % znr)
            return OrderedDict({'result': 'fail', 'sm_fail_reason': "Cant find znr in SM database"})
        soup = BeautifulSoup(options_xml, 'lxml')
        logging.info(soup.prettify())
        logging.info("Trying to get full_name, full_name_label and tub_num in OPTIONS field from %s" % znr)
        # Пытаемся взять информацию из полей, если их нет, считаем, что ЗНД не является корректной заявкой на доступ
        try:
            full_name = soup.findAll('option', id='accessUser_0')[0].string
            full_name_label = soup.findAll('option', id='accessUser_0')[0]['label']
            tab_number = soup.findAll('text', id='accessUserTabnum')[0].string
        except IndexError:
            logging.critical("Can't find required fields in %s" % znr)
            return OrderedDict({'result': 'fail', 'sm_fail_reason': "It looks like that it is not correct access request"})
        # У ЗНР на доступ к рабочим обласятм список ролей содержится в тэге dostRO_added_checkboxes
        # У ЗНР на доступ к детальному слою в тэге dostup_added_checkboxes
        # У ЗНР на доступ к ПСИ в тэге testSreda_added_checkboxes
        logging.info('full_name = %s' % full_name)
        logging.info('full_name_label = %s' % full_name_label)
        logging.info("Trying to get roles in OPTIONS field from %s" % znr)
        try:
            roles_to_add_none_formated = soup.findAll('text', id='dostRO_added_checkboxes')[0].string
        except IndexError:
            logging.info("Trying to get roles in OPTIONS field from %s" % znr)
            try:
                roles_to_add_none_formated = soup.findAll('text', id='dostup_added_checkboxes')[0].string
            except IndexError:
                try:
                    roles_to_add_none_formated = soup.findAll('text', id='testSreda_added_checkboxes')[0].string
                except IndexError:
                    logging.critical("Can't find block with roles in OPTIONS field from %s" % znr)
                    return OrderedDict({'result': 'fail',
                                        'sm_fail_reason': "It looks like that access request is not for access to teradata"})
                else:
                    system_type = 'test'
            else:
                system_type = 'prom'
        else:
            system_type = 'prom'
        # Форматируем список ролей, убираем цифры, скобки и инфо в скобках
        roles_to_add_formated = [re.sub(r' \([^)]*\)', '', re.sub(r'^[0-9]+\. ', '', item.lower())) for item in
                                 roles_to_add_none_formated.split('\n')]
        # Почему-то иногда добавляется лишняя пустая строка, убираем ее из спикса ролей
        roles_to_add_formated = [item for item in roles_to_add_formated if item != '']
        # Иногда ФИО содержится в селекторе label тэга с ид accessUser_0, иногда в значении самого тэга.
        # Проверяем на длину.
        true_full_name = full_name_label if len(re.sub(r'\([^)]*\)', '', full_name_label)) > len(full_name) else full_name
        user_dict = {'result': 'OK',
                     'surname': true_full_name.split()[0],
                     'first_name': true_full_name.split()[1],
                     'patronymic': true_full_name.split()[2],
                     'tab_number': tab_number,
                     'roles_to_add': roles_to_add_formated,
                     'znr_number': znr,
                     'system_type': system_type}
        logging.info("\n".join('{} - {}'.format(key, value) for key, value in user_dict.items()))
        return user_dict

    def send_mes(self, text=default_message_text, cc=default_cc, smtp_host="localhost", from_mes=default_from):
        """
        Отправка сообщения пользователю с учетными данными для входа
        :param text: текст письма
        :param cc: копия
        :param smtp_host: смтп-сервер хост
        :param from_mes: отправитель
        """
        pwd = 'Passw0rd_1234567890' if self.is_created else 'не изменялся'
        text = text % (self.znr_number, '\n'.join(self.added_roles), self.login, pwd)
        text = MIMEText(text)
        msg = MIMEMultipart()
        msg['Subject'] = 'Предоставление доступа по %s' % self.znr_number
        msg['From'] = from_mes
        to = self.user_alpha_email if self.user_alpha_email else self.user_omega_email
        if not to:
            return OrderedDict({'sent': False, 'fail_sent_reason': 'cant find user email in adressbook'})
        msg['To'] = to
        if cc:
            msg['Cc'] = ','.join(cc)
        msg.attach(text)
        with open('td_instruction.docx', 'rb') as instruction:
            part = MIMEApplication(instruction.read(), Name='td_instruction.docx')
        part['Content-Disposition'] = 'attachment; filename="td_instruction.docx"'
        msg.attach(part)
        server = smtplib.SMTP(smtp_host)
        try:
            server.sendmail(from_mes, cc + [to], msg.as_string())
        except Exception as e:
            logging.error('Cant send message to %s' % to)
            logging.error(str(e))
            return OrderedDict({'sent': False, 'fail_sent_reason': 'exception while sending email'})
        else:
            logging.info("message was sent")
            server.quit()
            return OrderedDict({'sent': True})


def main(znr):
    result_dict = {}
    logging.basicConfig(format=u'%(levelname)-8s[%(asctime)s] %(message)s', level=logging.INFO,
                        filename='teradata_user_manager.log')
    if znr is None or len(znr) != 11 or znr[:3] != 'ЗНР':
        logging.error('%s is not a valid znr number' % znr)
        result_dict['result'] = 'fail'
        result_dict['reason'] = 'Invalid ZNR number'
        return result_dict
    else:
        user, res = User.create_valid_user(znr=znr)
    if not user:
        return res
    logging.info(user.__repr__())
    if user.existing_user():
        res['existing_user'] = True
        res.update(user.grant_roles())
    else:
        res['existing_user'] = False
        creating_user = user.create_user()
        res.update(creating_user)
        if creating_user['created']:
            res.update(user.grant_roles())
    if user.added_roles:
        user.send_mes()
    return res


class Connect(object):
    def __init__(self):
        try:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            logging.critical(str(e))
        server = ('localhost', 10000)
        self.server_sock.bind(server)
        self.server_sock.listen(3)

    def listen_port(self):
        while True:
            conn, adr = self.server_sock.accept()
            znr = conn.recv(10000).decode('utf-8')
            result = main(znr)
            result = pickle.dumps(result)
            conn.send(result)
            conn.close()


connect = Connect()
connect.listen_port()
