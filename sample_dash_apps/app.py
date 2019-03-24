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
## initialize processor
processor = Processor(config.model_path,config.dictionary_path)
id2name = processor.get_id2name_map(config.id2name_path)
## get global historical data in memory
#topic_path = './dashboard/model_weights/Mallet_50_topics_with_country_year_2019_02_12.xlsx'
if os.path.exists(config.df_agg_pkl_path):
    print("Load agg historical from pkle")
    df_agg = pd.read_pickle(config.df_agg_pkl_path)
else:
    data_df = pd.read_excel(config.historical_data_path,'Document and Topic')
    df_agg = aggregate_doc_topic_distribution(data_df)

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
                ],className='row',style={'height':'120px','background-color':'#007bff'}),
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
                        dcc.Interval(id="interval", interval=50, n_intervals=0),
                    ]
                ,style={'display':'block','width':'80%','margin':'auto'}),
                            
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
                             'display':'block',
                             'padding':'15px',
                             'margin': 'auto'}),
            
            html.Div(id='controls-container',children=[],style={'display':'block'}),

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

def build_html_table(df,filename,date):
    res = html.Div([
                    html.H5(filename),
                    html.H6(datetime.datetime.fromtimestamp(date)),
            
                    dash_table.DataTable(
                        data=df.to_dict('rows'),
                        columns=[{'name': i, 'id': i} for i in df.columns]
                    ),
            
                    html.Hr(),  # horizontal line

                ])
    return res 

def parse_doc(contents, filename, date,processor=processor):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'docx' in filename.lower():
            # Assume that the user uploaded a docx file
            #res = read_doc(io.BytesIO(decoded))
            doc = processor.read_doc(io.BytesIO(decoded))
            ## get topic df
            topic_df = get_topic_df(processor,doc)
        else:
            return html.Div([
                'You much upload a word document. No other type of document is supported at this point.'
            ])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
                        
    #res = html.Div([html.Div("{}".format(i)) for i in res])
    res = build_html_table(topic_df,filename,date)
    return res

def create_graph(df,xaxis_name,yaxis_name,id2name):
    #df[xaxis_name]=df[xaxis_name].apply(lambda x: "Topic-"+str(x))
    df = copy.copy(df)
    df[xaxis_name]=df[xaxis_name].apply(lambda x: id2name[x])
    ## merge ids with same topic 
    df = df.groupby(xaxis_name).agg(sum)
    df.reset_index(inplace=True)
    df.sort_values(by=['content_size'],ascending=False,inplace=True)
    
    traces = [
            go.Bar(x=df[xaxis_name],
                   y=df[yaxis_name],
                   text=df[xaxis_name])
            ]
    go_layout = go.Layout(title='Document Topic Distribution',
                          xaxis={'title':xaxis_name,
                                 'categoryorder': 'array',
                                 'categoryarray': df[xaxis_name]},
                          yaxis={'title':yaxis_name},
                          hovermode='closest')
    
    res = {'data':traces,
           'layout':go_layout}
    return res

def create_sub_graph(df,xaxis_name,yaxis_name,id2name):
    df = copy.copy(df)
    topic_name = id2name[df['gensim_topic'].iloc[0]]
    df[xaxis_name]=df[xaxis_name].apply(lambda x: "_"+str(x)+"_")
    traces = [
            go.Bar(x=df[xaxis_name],
                   y=df[yaxis_name],
                   )
            ]
    go_layout = go.Layout(title='Topic: {}'.format(topic_name),
                          xaxis={'title':xaxis_name,
                                 'categoryorder': 'array',
                                 'categoryarray': df[xaxis_name]},
                          yaxis={'title':yaxis_name},
                          hovermode='closest')
    
    res = {'data':traces,
           'layout':go_layout}
    return res


def process_input_data(contents, filename, date,processor=processor):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    print(filename,file=sys.stdout)
    try:
        if 'docx' in filename.lower():
            # Assume that the user uploaded a docx file
            #res = read_doc(io.BytesIO(decoded))
            doc = processor.read_doc(io.BytesIO(decoded))
            ## get topic df
            topic_df = get_topic_df(processor,doc)
            data_store = {'doc_name':filename,
                            'doc_date':date,
                            'topic_df':topic_df.to_json(orient='split', date_format='iso')}
            return json.dumps(data_store)
            
        else:
            return html.Div([
                'You much upload a word document. No other type of document is supported at this point.'
            ])
    except Exception as e:
        print(e,file=sys.stdout)
        return html.Div([
            'There was an error processing this file.'
        ])
    
def create_all_sub_graph(figures):
    ## build the graph object 
    res = [
                html.Div([
                    dcc.Graph(id='subgraph-1',figure=figures[0]),
                    ## build the graph object 
                    dcc.Graph(id='subgraph-2',figure=figures[1])
                    ],style= {'width': '49%', 'display': 'inline-block'}),
            
                html.Div([
                    ## build the graph object 
                    dcc.Graph(id='subgraph-3',figure=figures[2]),
                    ## build the graph object 
                    dcc.Graph(id='subgraph-4',figure=figures[3])
                ],style= {'width': '49%', 'display': 'inline-block'})
        ]
    
    return res
    
    
def update_graph(contents, filename, date,processor=processor):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'docx' in filename.lower():
            # Assume that the user uploaded a docx file
            #res = read_doc(io.BytesIO(decoded))
            doc = processor.read_doc(io.BytesIO(decoded))
            ## get topic df
            topic_df = get_topic_df(processor,doc)
        else:
            return html.Div([
                'You much upload a word document. No other type of document is supported at this point.'
            ])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    print('chart create')
    res = create_graph(topic_df,'gensim_topic','content_size',id2name) 
    return res



#%%
@app.callback(Output('intermediate-value', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def store_temp_date(list_of_contents, list_of_names, list_of_dates):
    
    doc,doc_name,doc_date = list_of_contents[0],list_of_names[0],list_of_dates[0]
    res = process_input_data(doc,doc_name,doc_date)
    
    return res    

@app.callback(Output('intermediate-value-2', 'children'),
              [Input('intermediate-value', 'children')]
              )
def store_historical_dfs(json_data):
    datasets = json.loads(json_data)
    doc_name = datasets['doc_name']
    doc_date = datasets['doc_date']
    ## load data
    country_name = "Brazil"
    topic_df = pd.read_json(datasets['topic_df'], orient='split')
    temp = df_agg.loc[country_name,:].reset_index()
    lattest_year = temp['year'].unique()[-1]
    country_df = get_county_df(df_agg,country_name,lattest_year)
    ## get topic ids 
    topic_ids = get_top_topic_ids(country_df,topic_df,4)
    ## get ts dfs 
    ts_dfs = get_plot_df_list(topic_ids,df_agg,topic_df,country_name)
    
    data_store = {}
    for idx,d in enumerate(ts_dfs):
        data_store['df_'+str(idx)] = d.to_json(orient='split', date_format='iso')
    
    return json.dumps(data_store)


@app.callback(Output('controls-container2', 'children'),
              [Input('intermediate-value', 'children')]
              )
def update_graph_1(json_data):
    datasets = json.loads(json_data)
    doc_name = datasets['doc_name']
    doc_date = datasets['doc_date']
    topic_df = pd.read_json(datasets['topic_df'], orient='split')
    figure = create_graph(topic_df,'gensim_topic','content_size',id2name) 
    res = [dcc.Graph(id='topic-graph',figure=figure)]
    return res

@app.callback(Output('controls-container', 'children'),
              [Input('intermediate-value-2', 'children')]
              )
def update_all_sub_graph(json_data):
    datasets = json.loads(json_data)
    figures = []
    for i in range(4):
        df = pd.read_json(datasets['df_{}'.format(str(i))], orient='split')
        figure = create_sub_graph(df,'year','content_size_old',id2name) 
        figures.append(figure)
    
    res = create_all_sub_graph(figures)
    return res

@app.callback(Output("progress", "value"), 
              [Input("interval", "n_intervals")])
def advance_progress(n):
    return min(n % 110, 100)

#@app.callback(Output('controls-container', 'style'), 
#              [Input('intermediate-value', 'children')])
#def toggle_container1(data):
#    if data:
#        return {'display': 'block'}
#    else:
#        return {'display': 'none'}

if __name__ == '__main__':
    #app.run_server(port=8888, host='0.0.0.0', debug=True)
    app.run_server(debug=True)