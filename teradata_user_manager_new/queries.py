# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 11:17:45 2017

@author: 01550070
"""

sm_find_znr_query = """
    select "NUMBER" 
    from SMPRIMARY.SBREQUESTTASKM1
    where 1=1
    and rownum < 20
    and  ASSIGNEE_NAME = '%s'
    """

sm_get_znr_oprions_query = """
    select options 
    from SMPRIMARY.SBREQUESTTASKM1 
    where "NUMBER" = '%s'
    """

td_select_users_by_login = """
    select DatabaseName 
    from dbc.databases 
    where databasename = '%s' 
    and DBKind = 'U';
    """

td_select_user_by_alpha = """
    SELECT email.TD_USERNAME 
    FROM Tec_users_metha.mapping_email email
    JOIN dbc.databases db
    ON email.TD_USERNAME = db.databasename
    WHERE email.alpha_email = '%s'
    """

td_select_user_by_sigma = """
    SELECT email.TD_USERNAME 
    FROM Tec_users_metha.mapping_email email
    JOIN dbc.databases db
    ON email.TD_USERNAME = db.databasename
    WHERE email.sigma_email = '%s'
    """

td_grant_roles_query = """
    CALL SYS_UTILITIES.spGrantRole ('%s','%s');
    """


td_create_user = """
    CALL SYS_UTILITIES.spCreateUser ('%s', '',
                                     '%s', '%s', '%s','%s','%s','%s','%s' );
    """

adressbook_find_user_by_fio = """
    SELECT EmailAlpha, EmailSigma, Structure, EmployeeID, EmailOmega
    FROM view_OSPPR WHERE (LastName + FirstName + MiddleName) ='%s';
    """

adressbook_find_user_by_tab_number = """
    SELECT EmailAlpha, EmailSigma, Structure, EmployeeID, EmailOmega
    FROM view_OSPPR WHERE EmployeeID LIKE '%%%s%%';
    """

