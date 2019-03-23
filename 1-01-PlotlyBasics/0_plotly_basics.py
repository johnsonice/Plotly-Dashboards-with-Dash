
# coding: utf-8

# ### Plotly Basics

# In[3]:


#######
# This script creates a static matplotlib plot
######
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# create fake data:
df = pd.DataFrame(np.random.randn(100,4),columns='A B C D'.split())
df.plot()
plt.show()

# #### Simply line graph 

# In[14]:

#######
# This script creates the same type of plot as basic1.py,
# but in Plotly. Note that it creates an .html file!
######
import numpy as np
import pandas as pd
#import plotly.plotly as py
import plotly.offline as pyo

# create fake data:
df = pd.DataFrame(np.random.randn(100,4),columns='A B C D'.split())
pyo.plot([{
    'x': df.index,
    'y': df[col],
    'name': col
} for col in df.columns])


# #### Simple scatter plot

# In[3]:

#######
# This plots 100 random data points (set the seed to 42 to
# obtain the same points we do!) between 1 and 100 in both
# vertical and horizontal directions.
######
import plotly.offline as pyo
import plotly.graph_objs as go
import numpy as np

np.random.seed(42)
random_x = np.random.randint(1,101,100)
random_y = np.random.randint(1,101,100)

data = [go.Scatter(
    x = random_x,
    y = random_y,
    mode = 'markers',               ## passing additional options
    marker=dict(
        size=12,
        color='rgb(51,204,153)',
        symbol='pentagon',
        line={'width':2}
    )
)]

layout = go.Layout(title='Hello First Plot',
                   xaxis={'title':'My x Axis'},    ## just pass dictonary
                   yaxis=dict(title='My Y Axis'),  ## passing a dict, it is the same
                  hovermode='closest')  

fig = go.Figure(data=data,layout=layout)           ## create a figure object
pyo.plot(fig, filename='scatter1.html')            ## pass in the figure object


# #### Multiple line graph 

# In[11]:

import numpy as np
import plotly.offline as pyo
import plotly.graph_objs as go 
np.random.seed(56)

x_values = np.linspace(0,1,100)
y_values = np.random.randn(100)

trace0 = go.Scatter(x=x_values,y=y_values + 5,
                  mode = 'markers',name='markers')
trace1 = go.Scatter(x=x_values,y=y_values,
                   mode='lines',name='mylines')
trace2 = go.Scatter(x=x_values,y=y_values-5,
                   mode='lines+markers',name='mylines2')

data = [trace0,trace1,trace2]

lyout = go.Layout(title='Line Charts')
fig = go.Figure(data=data,layout=layout)
pyo.plot(fig,filename='line1.html') ## save to a html file 


# In[19]:

import pandas as pd
import plotly.offline as pyo
import plotly.graph_objs as go 

## read pandas form csv
df=pd.read_csv('../SourceData/nst-est2017-alldata.csv')
df.head()

## do some basic filtering
df2=df[df['DIVISION']=='1']
df2.set_index('NAME',inplace=True)
filter_cols = [col for col in df2.columns if col.startswith('POP')]
df2=df2[filter_cols]
df2.head()

## build data and plot it 
data = [go.Scatter(x=df2.columns,
                  y=df2.loc[name],
                  name=name) 
        for name in df2.index]
pyo.plot(data)

#%%
###########33#############
## create bar charts #####
##########################

import plotly.offline as pyo
import plotly.graph_objs as go
import pandas as pd

df = pd.read_csv('../SourceData/2018WinterOlympics.csv')

trace1 = go.Bar(x=df['NOC'],y=df['Gold'],
                name='Gold',marker={'color':'#FFD700'})
trace2 = go.Bar(x=df['NOC'],y=df['Silver'],
                name='Gold',marker={'color':'#9EA0A1'})
trace3 = go.Bar(x=df['NOC'],y=df['Bronze'],
                name='Gold',marker={'color':'#CD7F32'})

data = [trace1,trace2,trace3]
layout = go.Layout(title='Medals',barmode='stack')## bar mode default os grouped barbs
fig = go.Figure(data,layout)
pyo.plot(fig)

#%%
##### horizontal example bar 
# Perform imports here:
import plotly.offline as pyo
import plotly.graph_objs as go
import pandas as pd

# create a DataFrame from the .csv file:
df = pd.read_csv('../SourceData/mocksurvey.csv',index_col=0)

# create traces using a list comprehension:
data = [go.Bar(
    y = df.index,     # reverse your x- and y-axis assignments
    x = df[response],
    orientation='h',  # this line makes it horizontal!
    name=response
) for response in df.columns]

# create a layout, remember to set the barmode here
layout = go.Layout(
    title='Mock Survey Results',
    barmode='stack'
)

# create a fig from data & layout, and plot the fig.
fig = go.Figure(data=data, layout=layout)
pyo.plot(fig, filename='solution3b.html')







