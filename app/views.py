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

pw_path =  '/home/ryan/credentials/'
with open(os.path.join(pw_path, 'mysql_pw.txt')) as f:
    pw = f.read().strip('\n')
        
#db = mdb.connect(user="root", host="localhost", passwd=pw, db="world", charset='utf8')
db = mdb.connect(user="root", host="localhost", passwd=pw, db="gamepricepred", charset='utf8')
@app.route('/')
@app.route('/index')
def ss_input():
  return render_template("ssinput.html")
  

@app.route('/ssoutput')
def ss_output():
    game_id =  request.args.get('ID')
    
    with db:
        cur = db.cursor()
        #add try/except statements
        cur.execute("SELECT SteamDBTimestamp FROM Games WHERE Appid = %d;" % int(game_id))
        query_results = cur.fetchall()
        
    game_info = str(query_results[0]) #just return the first option

    appid= game_id
    x = np.array([1,2,3,4,5,6,7,8,9,10])
    y = np.array([1,2,3,4,5,6,7,8,9,10])
    graph_response = a_Model.graph_prices(x,y,'stuff')
    return render_template("ssoutput.html", game_info = game_info, appid = appid)

@app.route("/priceplot.png")
def priceplot():
    '''modified from example at https://gist.github.com/wilsaj/862153'''
    x = np.array([1,2,3,4,5,6,7,8,9,10])
    y = np.array([1,2,3,4,5,6,7,8,9,10])
    response = a_Model.graph_prices(x,y,'stuff')
    return response

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