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
import support
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
    game_id =  int(request.args.get('option'))
   
    appid= game_id    
    db2 = mdb.connect(user="root", host="localhost", passwd=pw, db="ssf_db", charset='utf8')
    with db2:
        cur = db2.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT * FROM website_table WHERE appid = %d" % appid)

    ginfo = cur.fetchone()
    gname = ginfo['game_name']
    adiscount = "%0.1f%%" % (ginfo['avg_discount'])
    asavings = "$%0.2f" % (ginfo['avg_savings'])
    sale_prob = ginfo['sale_prob_y']*100
    if sale_prob == 0:
        sale_prob = 1
    elif sale_prob == 100:
        sale_prob = 90
    
    cur_price_str,cur_price,on_sale_currently = support.get_current_price(appid)
            
    
    percent = "%0.1f%%" % (sale_prob)
    
    ## stand in for real code:
    if ginfo['sale_prob_y'] < 0.5:
        buy_time = 'buy %s now, since it is not likely to go on sale soon.' % (gname)
    else:
        buy_time = 'wait for a sale.'
        
    bottom_games = support.recommend_games(appid,float(cur_price.strip('$')))
    
    '''not really dry, but works for now'''    
    left_g = bottom_games[0] #left,center,right are the appids fed into the html template for the graphics call
    center_g = bottom_games[1]
    right_g = bottom_games[2]
    
    _cps, left_p, _osc = support.get_current_price(left_g)
    _cps, center_p, _osc = support.get_current_price(center_g)
    _cps, right_p, _osc = support.get_current_price(right_g)
    
    return render_template("ssoutput3.html", 
                           appid = appid,option_list = OPTION_LIST,
                           name = gname, discount = adiscount, 
                           savings = asavings, percent = percent,
                           buy_time = buy_time, cur_price_info = cur_price_str,
                           left_id = left_g, cent_id = center_g, 
                           right_id = right_g,
                           left_price = left_p, right_price = left_p,
                           center_price = center_p) #add back in "game info" later


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