# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 16:00:16 2015

@author: ryan

to limit the number of games to display for MVP presentation,
 we'll limit the number in the list to 500, selected from an excel file with boolean variable next to each game id
"""

import pymysql as mdb
import xlwt, xlrd
import numpy as np
import pickle

with open('db.pw') as f: #ignored in git
    pw = f.read().strip('\n')
db2 = mdb.connect(user="root", host="localhost", passwd=pw, db="ssf_db", charset='utf8')

with db2:
    cur = db2.cursor()
    cur.execute("SELECT game_name,appid FROM website_table")

OPTION_LIST = cur.fetchall()    
OPTION_LIST = sorted([{'name':x[0],'appid':x[1]} for x in OPTION_LIST],key=lambda k: k['name'] )

def make_workbook():
    '''make the work book which can be later edited'''
    workbook = xlwt.Workbook() 
    sheet = workbook.add_sheet("games") 
    
    for i,item in enumerate(OPTION_LIST):
        sheet.write(i,0,item['appid'])
        sheet.write(i,1,item['name'])
        sheet.write(i,2,0)
        
    workbook.save("use_games.xls")
    

def make_appid_list():
    '''make the app list from the workbook. This function should be called (for now)
    from the console'''
    workbook = xlrd.open_workbook('use_games.xls')
    sheet_names = workbook.sheet_names()
    xl_sheet = workbook.sheet_by_name(sheet_names[0])
    use_vals =  list(np.where(np.array(xl_sheet.col_values(2)) == 1)[0])
    app_ids = xl_sheet.col_values(0)
    use_appids = [int(app_ids[i]) for i in use_vals]
    with open("../use_appids.p",'wb') as f:
        pickle.dump(use_appids,f)
    



    