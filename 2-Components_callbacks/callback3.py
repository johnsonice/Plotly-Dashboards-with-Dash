#######
# Here we'll use the mpg.csv dataset to demonstrate
# how multiple inputs can affect the same graph.
######
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd


df = pd.read_csv('../SourceData/mpg.csv')
## mpg hp displace ....
features = df.columns

app = dash.Dash()

elements = [
        ## build two div for selection
                html.Div([
                        dcc.Dropdown(
                            id='xaxis',
                            options=[{'label': i.title(), 'value': i} for i in features],
                            value='displacement'
                        )
                    ],style={'width': '48%', 'display': 'inline-block'}),
                    
                html.Div([
                        dcc.Dropdown(
                            id='yaxis',
                            options=[{'label': i.title(), 'value': i} for i in features],
                            value='mpg'
                        )
                    ],style={'width': '48%', 'display': 'inline-block'}),
        ## build the graph object 
                dcc.Graph(id='feature-graphic')
            ]

app.layout = html.Div(elements,style={'padding':10})


@app.callback(
        Output('feature-graphic','figure'),
        [Input('xaxis','value'),
         Input('yaxis','value')]
        )
def update_graph(xaxis_name,yaxis_name):
    traces = [
            go.Scatter(x=df[xaxis_name],
                       y=df[yaxis_name],
                       text=df['name'],
                       mode='markers',
                       marker={'size':15,
                               'opacity':0.5,
                               'line':{'width':0.5,'color':'white'}},
                       )
            ]
    go_layout = go.Layout(title='My Dashboard for MPG',
                          xaxis={'title':xaxis_name},
                          yaxis={'title':yaxis_name},
                          hovermode='closest')
    
    res = {'data':traces,
           'layout':go_layout}
    return res


if __name__ == '__main__':
    app.run_server()


#%%
#app = dash.Dash()
#
#df = pd.read_csv('../data/mpg.csv')
#
#features = df.columns
#
#app.layout = html.Div([
#
#        html.Div([
#            dcc.Dropdown(
#                id='xaxis',
#                options=[{'label': i.title(), 'value': i} for i in features],
#                value='displacement'
#            )
#        ],
#        style={'width': '48%', 'display': 'inline-block'}),
#
#        html.Div([
#            dcc.Dropdown(
#                id='yaxis',
#                options=[{'label': i.title(), 'value': i} for i in features],
#                value='acceleration'
#            )
#        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
#
#    dcc.Graph(id='feature-graphic')
#], style={'padding':10})
#
#@app.callback(
#    Output('feature-graphic', 'figure'),
#    [Input('xaxis', 'value'),
#     Input('yaxis', 'value')])
#def update_graph(xaxis_name, yaxis_name):
#    return {
#        'data': [go.Scatter(
#            x=df[xaxis_name],
#            y=df[yaxis_name],
#            text=df['name'],
#            mode='markers',
#            marker={
#                'size': 15,
#                'opacity': 0.5,
#                'line': {'width': 0.5, 'color': 'white'}
#            }
#        )],
#        'layout': go.Layout(
#            xaxis={'title': xaxis_name.title()},
#            yaxis={'title': yaxis_name.title()},
#            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
#            hovermode='closest'
#        )
#    }
#
#if __name__ == '__main__':
#    app.run_server()
