# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 21:54:40 2017

@author: 01550070
"""

from tkinter import *
import tkinter.scrolledtext as ScrolledText
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import teradata
from teradata.api import DatabaseError
import win32com.client as win32
import logging
import pyodbc

from translit import translit
from roles_list import get_role
from send_mail import outlook_mail, unlock_mail


#VARS
select_users = "select DatabaseName from dbc.databases where databasename like '%s' and DBKind = 'U';"
add_user = "CALL SYS_UTILITIES.spCreateUser ('%s', 'Passw0rd_123', '%s', '%s', '%s','%s','%s','%s','%s' )"
grant_role = "CALL SYS_UTILITIES.spGrantRole ('%s', '%s')"
grant_logon = 'grant logon on all to "%s"'
unlock_query = "CALL SYS_UTILITIES.spChangeTemporaryPassword ('%s', '%s')"
select_postboxes_query = "SELECT EmailAlpha, EmailSigma, LastName, FirstName, MiddleName FROM view_OSPPR WHERE EmployeeID LIKE '%s';"



class FindUserVisualForm (Tk):
    def __init__(self, *args, **kwargs):
        self.addressbook_connection = pyodbc.connect('')
        self.addressbook_cursor = self.addressbook_connection.cursor()
        self.udaExec = teradata.UdaExec(appConfigFile="udaexec.ini")
        self.session = self.udaExec.connect("${dataSourceName}")
        Tk.__init__(self, *args, **kwargs)
        
        #MAIN FRAME
        self.geometry('800x815')
        self.resizable(True, True)
        self.user_insert_field = Entry(self, bd=5)
        self.find_user_button = Button(self, 
                                       bg='white', text='Найти пользователя',
                                       command=self.users_list)
        self.user_list = Listbox(self, selectmode=SINGLE )
        self.user_list_scrollbar = Scrollbar(self)
        self.user_insert_field.place(x=5, y=5, width=300, height=50)
        self.find_user_button.place(x=335, y=5, width=200, height=50)
        self.user_list.place(x=5, y=75, width=300, height=100)
        self.user_list_scrollbar.place(x=305, y=75, width=20, height=100)
        self.user_list_scrollbar['command'] = self.user_list.yview
        self.user_list['yscrollcommand'] = self.user_list_scrollbar.set
        self.user_insert_field.bind('<Button-3>', self.insert_into_user_find_field)
        self.log_panel = ScrolledText.ScrolledText(self, state='disabled')
        self.log_panel.place(x=5,y=650, width=790, height=160)
        self.var = IntVar()
        self.promtd_radio = Radiobutton(self, text="PromTD", variable=self.var, value=1, command=self.change_db)
        self.promtd_radio.place(x=600, y=5)
        self.pantd_radio = Radiobutton(self, text="PanTD", variable=self.var, value=2, command=self.change_db)
        self.pantd_radio.place(x=600, y=40)
        self.var.set(1)

        #USER_ADD_FRAME
        self.user_add_frame = Frame(self, bd=0, highlightbackground='black', 
                                    highlightcolor='black', highlightthickness=1)
        self.user_add_frame.place(x=5, y=200, width=795, height=125)
        self.create_user_label = Label (self.user_add_frame, 
                                        text='Создание нового пользователя', 
                                        font='Arial 13')
        self.create_user_label.place(x=5, y=5)
        self.terbank_choice = ttk.Combobox(self.user_add_frame, 
                                           values=['', 'BAB', 'CCH', 'DVB', 
                                           'PVB', 'SEV', 'SIB', 'SRB', 'SZB', 
                                           'UB', 'UZB', 'VVB', 'ZSB', 'ZUB'], height=13)
        self.terbank_choice.place(x=5,y=60, width=50, height=30)
        self.terbank_choice_label = Label (self.user_add_frame, text='ТБ', font='Arial 10')
        self.terbank_choice_label.place(x=15, y=35)
        self.user_login = Entry (self.user_add_frame)
        self.user_login.place (x=65, y=60, width=125, height=30)
        self.user_login_label = Label (self.user_add_frame, text='Логин', font='Arial 10')
        self.user_login_label.place(x=75, y=35)
        self.zno_num_field = Entry (self.user_add_frame)
        self.zno_num_field.place (x=200, y=60, width=85, height=30)
        self.zno_num_field_label = Label (self.user_add_frame, text='Номер ЗНД', font='Arial 10')
        self.zno_num_field_label.place(x=210, y=35)
        self.tab_number_field = Entry (self.user_add_frame)
        self.tab_number_field.place (x=295, y=60, width=65, height=30)
        self.tab_number_field_label = Label (self.user_add_frame, text='Таб.№', font='Arial 10')
        self.tab_number_field_label.place(x=305, y=35)
        self.alpha_email_field = Entry (self.user_add_frame, state='readonly')
        self.alpha_email_field.place(x=370, y=60, width=160, height=30)
        self.alpha_email_field_label = Label (self.user_add_frame, text='Почта Альфа', font='Arial 10')
        self.alpha_email_field_label.place(x=380, y=35)
        self.sigma_email_field = Entry (self.user_add_frame, state='readonly')
        self.sigma_email_field.place(x=540, y=60, width=160,height=30)
        self.sigma_email_field_label = Label (self.user_add_frame, text='Почта Сигма', font='Arial 10')
        self.sigma_email_field_label.place(x=550, y=35)
        self.button_to_add_user = Button(self.user_add_frame, bg='white', text='Создать', command=self.create_user)        
        self.button_to_add_user.place(x=710, y=60, width=70, height=30)        
        
        #GRANT_ROLES_FRAME
        self.grant_role_frame = Frame(self, bd=0, highlightbackground='black', 
                                    highlightcolor='black', highlightthickness=1)                                
        self.grant_role_frame.place(x=5, y=340, width=420, height=300)
        self.grant_role_frame_label = Label(self.grant_role_frame, text='Выдача прав', font='Arial 13')
        self.grant_role_frame_label.place(x=5, y=5)
        self.user_login_for_grant = Entry(self.grant_role_frame)
        self.user_login_for_grant.place (x=5, y=55, width=125, height=30)        
        self.user_login_for_grant_label = Label(self.grant_role_frame, text='Логин', font='Arial 10')
        self.user_login_for_grant_label.place(x=5, y=30)
        self.roles_list = Text(self.grant_role_frame)
        self.roles_list.place(x=5,y=120, width=405, height=160)
        self.roles_list_label = Label(self.grant_role_frame, text='Список ролей', font='Arial 10')
        self.roles_list_label.place(x=5,y=95)     
        self.button_to_grant_roles = Button(self.grant_role_frame, bg='white', text='Выдать', command=self.grant_roles )
        self.button_to_grant_roles.place(x=140, y=55, width=100, height=30)
        self.button_to_send_email = Button(self.grant_role_frame, bg='white', text='Отправить письмо', command=self.send_user_info)
        self.button_to_send_email.place(x=260, y=55, width=150, height=30)
        
        #UNLOCK_USER_FRAME
        self.unlock_user_frame = Frame(self, bd=0, highlightbackground='black', 
                                    highlightcolor='black', highlightthickness=1)                                
        self.unlock_user_frame.place(x=430,y=340, width=370, height=300)
        self.unlock_user_frame_label = Label(self.unlock_user_frame, text='Разблокировка пользователей', font='Arial 13')
        self.unlock_user_frame_label.place(x=5,y=5)
        self.user_login_for_unlock = Entry(self.unlock_user_frame)
        self.user_login_for_unlock_label = Label(self.unlock_user_frame, text='Логин:', font='Arial 10')
        self.user_pass_for_unlock = Entry(self.unlock_user_frame)
        self.user_pass_for_unlock.insert('insert', 'Passw0rd_123_4')
        self.user_pass_for_unlock_label = Label(self.unlock_user_frame, text='Пароль:', font='Arial 10')
        self.zno_for_unlock = Entry(self.unlock_user_frame)
        self.zno_for_unlock_label = Label(self.unlock_user_frame, text='По ЗНО:', font='Arial 10')
        self.user_login_for_unlock_label.place(x=5, y=45)
        self.user_pass_for_unlock_label.place(x=5,y=80)
        self.zno_for_unlock_label.place(x=5, y=115)
        self.user_login_for_unlock.place(x=75, y=45, width=125, height=25)        
        self.user_pass_for_unlock.place(x=75, y=80, width=125, height=25)
        self.zno_for_unlock.place(x=75, y=115, width=125, height=25)
        self.button_to_unlock_user = Button(self.unlock_user_frame, bg='white', text='Разблокировать', command=self.unlock_user )        
        self.button_to_unlock_user.place(x= 225, y=45, width=135, height=25)
        self.button_to_send_unlock_mail = Button(self.unlock_user_frame, bg='white', text='Отправить письмо', command=self.send_unlock_email)
        self.button_to_send_unlock_mail.place(x=225, y=80, width=135, height=25)
        
    def insert_into_user_find_field(self, *args):
        clipboard = self.clipboard_get()
        self.user_insert_field.insert('insert', clipboard)
        
    def users_list(self, *args):
        l = []
        str_to_find = ''
        fio_rus = self.user_insert_field.get()
        trans_fio = translit(fio_rus).title()
        list_of_fio = trans_fio.split()
        sername = list_of_fio[0]        
        str_to_insert = '%' + sername + '%'
        str_to_find = select_users %str_to_insert
        self.user_list.delete(0, END)
        for row in self.session.execute(str_to_find):
            l.append(row['DatabaseName'])
        for item in l:
            self.user_list.insert(END, item)
        try:
            login = list_of_fio[0] + '-' + list_of_fio[1][0] + list_of_fio[2][0]
        except IndexError:
            login = list_of_fio[0]
        for child in self.user_add_frame.winfo_children():
            if child.winfo_class() == 'Entry':
                child.delete(0, END)
            self.insert_into_alpha_email_field('')
            self.insert_into_sigma_email_field('')
        self.user_login.insert('insert', login)
        self.user_login_for_grant.delete(0, END)
        
    def insert_into_alpha_email_field(self, value):
        self.alpha_email_field.configure(state='normal')
        self.alpha_email_field.delete(0, END)
        self.alpha_email_field.insert(0, value)
        self.alpha_email_field.configure(state='readonly')
        
    def insert_into_sigma_email_field(self, value):
        self.sigma_email_field.configure(state='normal')
        self.sigma_email_field.delete(0, END)
        self.sigma_email_field.insert(0, value)
        self.sigma_email_field.configure(state='readonly')

        
    def create_user(self, *args):
        if self.tab_number_field.get() == '':
            messagebox.showinfo('Ошибка','Не указан табельный номер сотрудника')
            return None
        if self.user_login.get() == '':
            messagebox.showinfo('Ошибка','Не указан логин сотрудника')
            return None
        if self.zno_num_field.get() == '':
            messagebox.showinfo('Ошибка','Не номер ЗНО, по которому предоставляется доступ')
            return None
        result_from_query_to_addressbook = self.addressbook_cursor.execute(select_postboxes_query 
                                                                            %("%" + self.tab_number_field.get() + "%"))
        if result_from_query_to_addressbook.rowcount == 0:
            messagebox.showerror('Ошибка', 'Сотрудника с таким табельным номером не найдено в базе данных телефонного справочника')
            return None        
        else:
            row = result_from_query_to_addressbook.fetchone()
        alpha_email = row[0]
        sigma_email = row[1]
        lastname = row[2]
        firstname = row[3]
        midlename = row[4]
        self.insert_into_alpha_email_field(alpha_email)
        self.insert_into_sigma_email_field(sigma_email)
        
        alpha_login = ''
        login = self.terbank_choice.get() + '-' + self.user_login.get() if self.terbank_choice.get() != '' else self.user_login.get()
        for i in self.alpha_email_field.get():
            if i == '@':
                break
            else:
                alpha_login += i
        self.user_login_for_grant.delete(0, END)
        self.user_login_for_grant.insert('insert', login)
        row_to_execute = add_user %(login, 
                                    self.zno_num_field.get() + '.' + self.tab_number_field.get(), 
                                    alpha_login, self.alpha_email_field.get(), 
                                    self.sigma_email_field.get(), lastname, firstname, midlename)
        print(row_to_execute)
#        self.session.execute(row_to_execute)
#        self.user_login_for_grant.delete(0, END)
        
        
    def grant_roles(self, *args):
        roles = get_role(self.roles_list.get('1.0', END))
        roles_to_grant = roles["ok"]
        if roles["error"]:
            logger.error("ERROR: Can't find some roles in roles_list.py:" + ", ".join(roles["error"]))
        for role in roles_to_grant:
            str_to_grant = grant_role %(self.user_login_for_grant.get(), role)
            try:
                self.session.execute(str_to_grant)
            except DatabaseError:
                logger.error("ERROR: User %s or role %s does not exists in current db" %(self.user_login_for_grant.get(), role))
            
    def send_user_info(self, *args):
        if self.alpha_email_field.get() != '':
            rec = self.alpha_email_field.get()
        else:
            rec = self.user_insert_field.get()
        if self.tab_number_field.get() == '':
            password = 'Не изменялся'
        else:
            password = 'Passw0rd_123'
        outlook_mail(rec, self.zno_num_field.get(), 
                     self.roles_list.get('1.0', END), self.user_login_for_grant.get(), password)
                     
    def unlock_user (self, *args):
        name = self.user_login_for_unlock.get()
        password = self.user_pass_for_unlock.get()
        grant_exec = grant_logon %name
        unlock_exec = unlock_query %(name, password)
        self.session.execute(grant_exec)
        self.session.execute(unlock_exec)
    
    def send_unlock_email(self, *args):
        name = self.user_login_for_unlock.get()
        password = self.user_pass_for_unlock.get()
        zno = self.zno_for_unlock.get()
        rec=self.user_insert_field.get()
        unlock_mail(rec, zno, name, password)
        
    def quit_window(self):
        self.destroy()
        gui_handler.close()
        logger.handlers = []
        
    def change_db(self, *args):
        self.session.close()
        conf = "pantd.ini" if self.var.get() == 2 else "udaexec.ini"
        self.udaExec = teradata.UdaExec (appConfigFile=conf)
        self.session = self.udaExec.connect("${dataSourceName}")
    
        


class TextHandler(logging.StreamHandler):
    def __init__(self, text):
        logging.StreamHandler.__init__(self)
        self.text = text
        
    def emit (self, record):
        msg = self.format(record)
        self.text.config(state='normal')
        self.text.insert("end", msg + "\n")
        self.flush()
        self.text.config(state='disabled')
                

if __name__ == '__main__':
    app = FindUserVisualForm()
    app.title('TERADATA USER MANAGER')
    logging.basicConfig(format=u'%(levelname)-8s[%(asctime)s] %(message)s', level=logging.INFO)
    logger = logging.getLogger()
    gui_handler = TextHandler(app.log_panel)
    logger.addHandler(gui_handler)
    logger.info('LOG:')
    app.protocol("WM_DELETE_WINDOW", app.quit_window)
    app.mainloop()
