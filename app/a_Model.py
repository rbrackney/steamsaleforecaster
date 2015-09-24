# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 12:29:31 2015

@author: ryan
"""

import matplotlib.pyplot as plt
import numpy as np
import datetime
import StringIO
import random
import matplotlib.dates as md
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter

from flask import make_response

def modelit(fromUser  = 'Default', population = 0):
    print 'The population is %i' % population
    result = population/1000000.0
    if fromUser != 'Default':
        return result
    else:
        return 'check your input'

def graph_prices(x, y, gname):
    
    
    x_list = list(x)
    x_dt =  [datetime.fromtimestamp(xx) for xx in x_list]
    fig=Figure(facecolor='white')
    ax=fig.add_subplot(111)
    ax.plot(x_dt,y,'r-')    
    ax.set_ylim([0,np.max(y) + np.max(y) * 0.10])
    #ax.set_title(gname)
    #ax.set_axis_bgcolor('red')

    formatter = FuncFormatter(money_format)
    ax.yaxis.set_major_formatter(formatter)
    #fig.autofmt_xdate()
    #xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    #ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    
    canvas=FigureCanvas(fig)
    png_output = StringIO.StringIO()
    canvas.print_png(png_output)
    response=make_response(png_output.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response
    
def money_format(x, pos):
    'The two args are the value and tick position'
    return '$%1.2f' % (x)
