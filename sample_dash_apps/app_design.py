import base64
import datetime
import io
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from docx import Document
import pandas as pd
import json 
import copy

import os
import sys
sys.path.insert(0,'./dashboard')
from process_util import Processor
from evaluate import get_topic_df
from graph_historical_util import get_county_df,get_top_topic_ids,get_plot_df_list,aggregate_doc_topic_distribution
import config

#%%

## load dash style
external_stylesheets = [dbc.themes.BOOTSTRAP,'https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.requests_pathname_prefix = ''


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Link", href="#")),
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="Menu",
            children=[
                dbc.DropdownMenuItem("Entry 1"),
                dbc.DropdownMenuItem("Entry 2"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Entry 3"),
            ],
        ),
    ],
    brand='SPR Review Document Topic Analysis',
    brand_href="#",
    sticky="top",
)

img_path = './dashboard/src/imf_seal.png'
def encode_image(image_file):
    encoded = base64.b64encode(open(image_file, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded.decode())

elements = [
            html.Div([
                html.Div([
                    html.Div([
                        html.Img(src=encode_image(img_path),
                                 style={'color': '#2c2825','height':'100%'}),
                    ],style={'width':'20%','margin':'10 auto','textAlign': 'center',}),
    
                    html.H2(
                        children='SPR Review Document Topic Analysis',
                        style={
                            'width':'60%',
                            'textAlign': 'center',
                            'padding-top':'25px',
                            'color':'white'
                        }
                    )
                ],className='row',style={'height':'120px','background-color':'#66b3ff'}),
            ],style={'margin':'25px 10px 40px 10px','borderRadius': '15px'}),
            
            dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                        ]),
                    style={
                        'width': '90%',
                        'height': '80px',
                        'lineHeight': '80px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'background-color':'#cccccc',
                        'opacity':'.3',
                        'margin': 'auto auto 40px auto'
                        },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
             html.Div(
                    [
                        dbc.Progress(id="progress", value=0, striped=True, animated=True),
                        dcc.Interval(id="interval", interval=250, n_intervals=0),
                    ]
                ,style={'display':'none'}),
                            
            html.Div(children=[
                    html.H5('Hot Button Issues Checklist:',
                            style={'margin': '5px',
                                   'padding':'5px',
                                   }),
                    dcc.Checklist(
                        options=[
                            {'label': 'Capital flow management', 'value': 'CFM'},
                            {'label': 'Exchange restrictions', 'value': 'ER'},
                            {'label': 'Multiple currency practice', 'value': 'MCP'},
                            {'label': 'Corruption', 'value': 'CROP'},
                            {'label': 'Governance', 'value': 'GOV'},
                            {'label': 'Fintech/digital', 'value': 'FD'},
                            {'label': 'Macroprudential measures', 'value': 'MPM'},
                            {'label': 'Housing', 'value': 'HOU'},
                            {'label': 'Demographic', 'value': 'DEM'},
                            {'label': 'Shadow banking', 'value': 'SB'},
                            {'label': 'Competition policy', 'value': 'CP'},
                            {'label': 'Foreign Exchange intervention', 'value': 'FEI'},
                            {'label': 'Belt and road', 'value': 'BNR'},
                            {'label': 'Arrears', 'value': 'ARR'},
                            {'label': 'Debt restructuring', 'value': 'DR'},
                            {'label': 'Financing assurances', 'value': 'FA'}
                        ],
                        values=['CFM', 'ER'],
                        labelStyle={'display': 'inline-block',
                                    'padding':"10px",
                                    'width':'23.5%',
                                    'borderWidth':'1px',
                                    'margin':'6px',
                                    'borderRadius': '5px',
                                    'borderStyle': 'solid'
                                    }
                    )
                    ],style={'width': '100%','margin': '10px'}
            ),
            
            ## build the graph object 
            html.Div(id='controls-container2',
                     #children=[dcc.Graph(id='topic-graph')],
                     style={'width':'100%',
                             'display':'none',
                             'padding':'15px',
                             'margin': 'auto'}),
            
            html.Div(id='controls-container',children=[

                ## build the graph object 
                html.Div([
                    dcc.Graph(id='subgraph-1'),
                    ## build the graph object 
                    dcc.Graph(id='subgraph-2')
                    ],style= {'width': '49%', 'display': 'inline-block'}),
    
                html.Div([
                    ## build the graph object 
                    dcc.Graph(id='subgraph-3'),
                    ## build the graph object 
                    dcc.Graph(id='subgraph-4')
                ],style= {'width': '49%', 'display': 'inline-block'}),
            ],style={'display':'none'}),

#            ## build table object
#            html.Div(id='output-data-upload',style={'width': '50%',
#                                                    'margin': 'auto',
#                                                    'padding':'50px'}),
            ## store intemediate data
            html.Div(id='intermediate-value',style={'display': 'none'}),
            html.Div(id='intermediate-value-2',style={'display': 'none'}),
        ]

app.layout = html.Div(elements,className='container',style={'max-width': '80%'})

#%%

if __name__ == '__main__':
    #app.run_server(port=8888, host='0.0.0.0', debug=True)
    app.run_server(debug=True)