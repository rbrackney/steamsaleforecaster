# -*- coding: utf-8 -*-
"""
Support functions for views.py
Created on Mon Sep 28 14:53:14 2015
@author: ryan


"""

from scipy import stats
import requests
import pymysql as mdb
import numpy as np

with open('db.pw') as f: 
    pw = f.read().strip('\n')    
db2 = mdb.connect(user="root", host="localhost", passwd=pw, db="ssf_db", charset='utf8')

def get_current_price(appid_in):
    '''get most current price from a game, then output it's current value'''
    site = 'http://store.steampowered.com/api/appdetails?appids=%d' % appid_in
    r = requests.get(site)
    the_json  = r.json()
    
    data = the_json[str(appid_in)]['data'][u'price_overview']
    disc = data['discount_percent']
    ip =  "$%0.2f" % (data['initial'] * .01)
    fp =  "$%0.2f" % (data['final'] * .01)
    discount_percent = "%d%%" % (disc)
    onsale = disc > 0
    if  onsale:
        out_str = 'is currently on sale for %s at %s %% off' % (fp, disc)
    else:
        out_str = 'is currently %s' % fp
    return out_str,fp, onsale
    
def rec_val(disc_amount,x):
    loc_base =0.5 #default center
    disc_mod = 0.01 #how much to shift the discount amount by
    loc_mod = disc_amount * disc_mod 
    loc = loc_base - loc_mod #shift the center by loc_amount
    y_l = stats.logistic.cdf(x, loc=loc, scale=.1)
    return y_l
    
def recommend_games(cur_appid, cur_price):
    '''looks in the database for games in the same cluster, but costing equal to
    or less than the current app, and presents them on the screen'''
    with db2:
        cur = db2.cursor(mdb.cursors.DictCursor)
        #get_cur_game_str = 
        cur.execute("SELECT * FROM cluster_price WHERE appid = %d" % (cur_appid))
        row_dict = cur.fetchone()
    cur_cluster = row_dict['cluster']
    
    with db2:
        cur = db2.cursor(mdb.cursors.DictCursor)
        cur.execute("SELECT * FROM cluster_price WHERE cluster = %d AND median_initial_price <= %f" % (cur_cluster, cur_price))
        
    criterion_games = cur.fetchall()
    ind_arr = np.arange(len(criterion_games))
    select_n =  3
    selected_games =  np.random.choice(ind_arr,select_n, replace = False)
    
    selected_game_ids = [criterion_games[i]['appid'] for i in selected_games]
    return selected_game_ids