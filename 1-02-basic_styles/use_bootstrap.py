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
# Boostrap CSS.
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})  # noqa: E501

elements = [
        ## build two div for selection
        
                html.Div([    
                        html.Div(['[]'],className='two columns',style={'opacity':'0'}), ## transparent place holder
                        html.Div([
                                dcc.Dropdown(
                                    id='xaxis',
                                    options=[{'label': i.title(), 'value': i} for i in features],
                                    value='displacement'
                                )
                            ],className='four columns'),
                        html.Div([
                                dcc.Dropdown(
                                    id='yaxis',
                                    options=[{'label': i.title(), 'value': i} for i in features],
                                    value='mpg'
                                )
                            ],className='four columns'),          
                ],className='row'),

                                    
            ## build the graph object 
                html.Div([
                    html.Div([
                            dcc.Graph(id='feature-graphic-1')
                    ],className="six columns"),
        
                    html.Div([
                            dcc.Graph(id='feature-graphic-2')
                    ],className="six columns")
                ],className='row')

            ]

app.layout = html.Div(elements,style={'padding':'5px'})


@app.callback(
        Output('feature-graphic-1','figure'),
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

@app.callback(
        Output('feature-graphic-2','figure'),
        [Input('xaxis','value'),
         Input('yaxis','value')]
        )
def update_graph2(xaxis_name,yaxis_name):
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
#%%
if __name__ == '__main__':
    app.run_server(debug=True)

