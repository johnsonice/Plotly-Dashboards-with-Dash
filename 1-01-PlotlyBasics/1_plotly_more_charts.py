#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 16:17:40 2019

@author: chengyu
"""

#########################
## Bubble chrats ########
#########################

# Perform imports here:
import plotly.offline as pyo
import plotly.graph_objs as go
import pandas as pd

df = pd.read_csv('../SourceData/mpg.csv')
df.head()

df['text1']=pd.Series(df['model_year'],dtype=str)
df['text2']="'"+df['text1']+" "+df['name']

data=[go.Scatter(x=df['horsepower'],
                 y=df['mpg'],
                 text=df['text2'],
                 mode='markers',
                 marker = dict(size=2*df['cylinders'],
                               color=df['weight'],
                               showscale=True),  ## give the size of the marker
                 
                 )]
layout = go.Layout( 
        title='Vehicle mpg vs. horsepower',
        xaxis = dict(title = 'displacement'),
        yaxis = dict(title = 'acceleration = seconds to reach 60mph'),
        hovermode='closest')
fig=go.Figure(data,layout)
pyo.plot(fig,filename='bar4.html')

#%%
###########################
### box plot ##############
###########################

import plotly.offline as pyo
import plotly.graph_objs as go

snodgrass = [.209,.205,.196,.210,.202,.207,.224,.223,.220,.201]
twain = [.225,.262,.217,.240,.230,.229,.235,.217]

data = [
    go.Box(
        y=snodgrass,
        boxpoints='all',  ## show all the dots 
        jitter=0.3,  ## spread out the data
        pointpos=-2.0, ## left and right of the dots position 
        name='QCS'
    ),
    go.Box(
        y=twain,
        name='MT'
    )
]
layout = go.Layout(
    title = 'Comparison of three-letter-word frequencies<br>\
    between Quintus Curtius Snodgrass and Mark Twain'
)
fig = go.Figure(data=data, layout=layout)
pyo.plot(fig, filename='box3.html')

#%%
##########################
## histograms
##########################


df = pd.read_csv('../SourceData/mpg.csv')

data = [go.Histogram(
            x=df['mpg'],
            xbins=dict(start=0,end=50,size=10),
            #nbinsx=60,
            ),
        go.Histogram(
                    x=df['cylinders'],
                    xbins=dict(start=0,end=50,size=10),
                    #nbinsx=60,
                    ),
        ]

layout = go.Layout(
    title="Number of presses per timeslot",
    barmode='stack'
)
fig = go.Figure(data=data, layout=layout)
pyo.plot(fig, filename='button_presses2.html')


#%%
##################
## distribution plot
#################333
import plotly.offline as pyo
import plotly.figure_factory as ff
import pandas as pd
import numpy as np

x1 = np.random.randn(1000)-2
x2 = np.random.randn(1000)
x3 = np.random.randn(1000)+2
x4 = np.random.randn(1000)+4
hist_data = [x1,x2,x3,x4]
group_labels=['x1','x2','x3','x4']
fig = ff.create_distplot(hist_data,
                         group_labels,
                         bin_size=[.2,.5,1,2]) ## different bin size
pyo.plot(fig,filename='distplot.html')

#%%
#################
## heat maps
#################


import plotly.offline as pyo
import plotly.graph_objs as go
from plotly import tools       ## used to creat sub plots 
import pandas as pd

df1 = pd.read_csv('../SourceData/2010SitkaAK.csv')
df2 = pd.read_csv('../SourceData/2010SantaBarbaraCA.csv')
df3 = pd.read_csv('../SourceData/2010YumaAZ.csv')

trace1 = go.Heatmap(
    x=df1['DAY'],
    y=df1['LST_TIME'],
    z=df1['T_HR_AVG'],
    colorscale='Jet',
    zmin = 5, zmax = 40 # add max/min color values to make each plot consistent
)
trace2 = go.Heatmap(
    x=df2['DAY'],
    y=df2['LST_TIME'],
    z=df2['T_HR_AVG'],
    colorscale='Jet',
    zmin = 5, zmax = 40
)
trace3 = go.Heatmap(
    x=df3['DAY'],
    y=df3['LST_TIME'],
    z=df3['T_HR_AVG'],
    colorscale='Jet',
    zmin = 5, zmax = 40
)

fig = tools.make_subplots(rows=1, cols=3,  ## layout 1 row 3 columns 
    subplot_titles=('Sitka, AK','Santa Barbara, CA', 'Yuma, AZ'),
    shared_yaxes = True,  # this makes the hours appear only on the left
)
fig.append_trace(trace1, 1, 1)
fig.append_trace(trace2, 1, 2)
fig.append_trace(trace3, 1, 3)

fig['layout'].update(      # access the layout directly!
    title='Hourly Temperatures, June 1-7, 2010'
)
pyo.plot(fig, filename='AllThree.html')






