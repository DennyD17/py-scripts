# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 23:23:59 2017

@author: 01550070
"""
def translit (str_to_translit):
    translited_str = ''   
    username_rus  = ''
    str_to_translit = str_to_translit.lower()    
    alphabet = {
    'а':'a',
    'б':'b',
    'в':'v',
    'г':'g',
    'д':'d',
    'е':'e',
    'ж':'j',
    'з':'z',
    'и':'i',
    'й':'i',
    'к':'k',
    'л':'l',
    'м':'m',
    'н':'n',
    'о':'o',
    'п':'p',
    'р':'r',
    'с':'s',
    'т':'t',
    'у':'u',
    'ф':'f',
    'х':'h',
    'ц':'c',
    'ч':'ch',
    'ш':'sh',
    'щ':'shc',
    'ъ':'',
    'ы':'i',
    'ь':'',
    'э':'e',
    'ю':'yu',
    'я':'ya',
    }        
    for symbol in str_to_translit:
        try:
            translited_str += alphabet[symbol]
        except KeyError:
            translited_str += symbol
    
    return translited_str
