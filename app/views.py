# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 10:55:30 2015

@author: ryan
"""
from flask import render_template, request, make_response
from app import app
import os
import pymysql as mdb
import a_Model
import numpy as np

with open('db.pw') as f: #ignored in git
    pw = f.read().strip('\n')


#db = mdb.connect(user="root", host="localhost", passwd=pw, db="gamepricepred", charset='utf8') #removed for now
db2 = mdb.connect(user="root", host="localhost", passwd=pw, db="ssf_db", charset='utf8')

with db2:
    cur = db2.cursor()
    cur.execute("SELECT game_name,appid FROM website_table")

OPTION_LIST = cur.fetchall()    
#option_list = sorted([x[0] for x in option_list])
OPTION_LIST = sorted([{'name':x[0],'appid':x[1]} for x in OPTION_LIST],key=lambda k: k['name'] )

@app.route('/')
@app.route('/index')
def ss_input():
    #db2 = mdb.connect(user="root", host="localhost", passwd='hats', db="ssf_db", charset='utf8')
    
    return render_template("ssinput.html",option_list = OPTION_LIST) #currently the index  

@app.route('/ssoutput')
def ss_output():
    #game_id =  request.args.get('ID')
    game_id =  int(request.args.get('option'))
    with db:
        cur = db.cursor()
        #add try/except statements
        cur.execute("SELECT SteamDBTimestamp FROM Games WHERE Appid = %d;" % int(game_id))
        query_results = cur.fetchall()
        
    game_info = str(query_results[0]) #just return the first option

    appid= game_id
    
    db2 = mdb.connect(user="root", host="localhost", passwd=pw, db="ssf_db", charset='utf8')
    with db2:
        cur = db2.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT * FROM website_table WHERE appid = %d" % appid)

    ginfo = cur.fetchone()
    gname = ginfo['game_name']
    adiscount = "%0.1f%%" % (ginfo['avg_discount'])
    asavings = "$%0.2f" % (ginfo['avg_savings']) 
    percent = "%0.1f%%" % (ginfo['sale_prob_y']*100)
    
    ## stand in for real code:
    if ginfo['sale_prob_y'] < 0.5:
        buy_time = 'buy it now, since it is not likely to go on sale soon.'
    else:
        buy_time = 'wait for a sale.'
    
    return render_template("ssoutput.html", game_info = game_info, 
                           appid = appid,option_list = OPTION_LIST,
                           name = gname, discount = adiscount, 
                           savings = asavings, percent = percent,
                           buy_time = buy_time)


@app.route("/<appid>/priceplot.png")
def priceplot2(appid):    
    with db:
        cur = db.cursor()
        cur.execute("SELECT plot_x FROM Games WHERE Appid = %d;" % int(appid))
        query_results = cur.fetchall()
        p_x = str(query_results[0])
        cur.execute("SELECT plot_y FROM Games WHERE Appid = %d;" % int(appid))
        query_results = cur.fetchall()
        p_y = str(query_results[0])
        print 'reached here'
        x = np.array(eval(eval(p_x[1:-2])))
        y = np.array(eval(eval(p_y[1:-2])))
        print 'and reached here'
        print type(x)
    #x = np.array([1,2,3,4,5,6,7,8,9,10])
    #y = np.array([1,2,3,4,5,6,7,8,9,10])
    response = a_Model.graph_prices(x,y,appid)
    return response