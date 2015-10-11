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
import pickle
print os.getcwd()

with open('db.pw') as f: #ignored in git
    pw = f.read().strip('\n')


#db = mdb.connect(user="root", host="localhost", passwd=pw, db="gamepricepred", charset='utf8') #removed for now
db2 = mdb.connect(user="root", host="localhost", passwd=pw, db="ssf_db", charset='utf8')

with db2:
    cur = db2.cursor()
    cur.execute("SELECT game_name,appid FROM website_table")


OPTION_LIST_ALL = cur.fetchall()    
OPTION_LIST_ALL = sorted([{'name':x[0],'appid':x[1]} for x in OPTION_LIST_ALL],key=lambda k: k['name'] )

OPTION_LIST =  list()

USE_APPIDS = pickle.load(open( "use_appids.p", "rb" ))
    
for i in OPTION_LIST_ALL:
    if i['appid'] in USE_APPIDS:
        OPTION_LIST.append(i)

@app.route('/')
@app.route('/index')
def ss_input():
    #db2 = mdb.connect(user="root", host="localhost", passwd='hats', db="ssf_db", charset='utf8')
    bottom_games, alternatives = support.recommend_games(10,60.00)
    
    '''not really dry, but works for now'''    
    left_g = bottom_games[0] #left,center,right are the appids fed into the html template for the graphics call
    center_g = bottom_games[1]
    right_g = bottom_games[2]
    
    _cps, left_p, _dc, _osc = support.get_rec_price(left_g,alternatives)
    _cps, center_p, _dc, _osc = support.get_rec_price(center_g,alternatives)
    _cps, right_p, _dc, _osc = support.get_rec_price(right_g,alternatives)
    
    return render_template("ssinput.html",left_id = left_g, cent_id = center_g, 
                           right_id = right_g,left_price = left_p, right_price = left_p,
                           center_price = center_p,
                           option_list = OPTION_LIST) #currently the index  

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
    
    cur_price_str,cur_price,cur_disc, on_sale_currently = support.get_current_price(appid)
            
    
    percent = "%0.1f%%" % (sale_prob)
    if percent == '1.0%':
        percent = '< 1%'
    
    ## stand in for real code:
    print sale_prob
    recomendation_score = support.rec_val(ginfo['avg_savings'],sale_prob * 0.01)
    print recomendation_score
    if recomendation_score < 0.5:
        buy_time = 'buy %s now, since it is not likely to go on sale soon.' % (gname)
    else:
        buy_time = 'wait for a sale.'
        
    bottom_games, alternatives = support.recommend_games(appid,float(cur_price.strip('$')))
    
    '''not really dry, but works for now'''    
    left_g = bottom_games[0] #left,center,right are the appids fed into the html template for the graphics call
    center_g = bottom_games[1]
    right_g = bottom_games[2]
    
    _cps, left_p, _dc, _osc = support.get_rec_price(left_g,alternatives)
    _cps, center_p, _dc, _osc = support.get_rec_price(center_g,alternatives)
    _cps, right_p, _dc, _osc = support.get_rec_price(right_g,alternatives)
    
    return render_template("ssoutput3.html", 
                           appid = appid,option_list = OPTION_LIST,
                           name = gname, discount = adiscount, 
                           savings = asavings, percent = percent,
                           buy_time = buy_time, cur_discount = cur_disc,
                           cur_price = cur_price,
                           left_id = left_g, cent_id = center_g, 
                           right_id = right_g,
                           left_price = left_p, right_price = right_p,
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