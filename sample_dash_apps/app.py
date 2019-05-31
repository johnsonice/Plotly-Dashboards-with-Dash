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
import time

import os
import sys
sys.path.insert(0,'./dashboard')
from process_util import Processor
from evaluate import get_topic_df
from graph_historical_util import get_county_df,get_top_topic_ids,get_plot_df_list,aggregate_doc_topic_distribution
import config
#%%
## initialize processor
processor = Processor(config.model_path,
                      config.dictionary_path,
                      config.country_map_path,
                      config.hot_button_file_path,
                      config.hot_button_dict_path,
                      config.adhoc_check_file_path,
                      config.adhoc_check_dict_path)

id2name = processor.get_id2name_map(config.id2name_path)
## get global historical data in memory
#topic_path = './dashboard/model_weights/Mallet_50_topics_with_country_year_2019_02_12.xlsx'
if os.path.exists(config.df_agg_pkl_path):
    print("Load agg historical from pkle")
    df_agg = pd.read_pickle(config.df_agg_pkl_path)
else:
    print('Generate agg historical df data and save as pickle ...')
    data_df = pd.read_excel(config.historical_data_path,'Document and Topic')
    df_agg = aggregate_doc_topic_distribution(data_df)
    df_agg.to_pickle(config.df_agg_pkl_path)
    
#%%
## get country drop down content 
countries = df_agg.index.get_level_values(0).unique().to_list()
country_dropdown_data = [{'label':c,'value':c} for c in countries]

## get hotbutton issue list 
hotbutton_issues = list(processor.hot_button_finder.hot_button_dict.keys())
hotbutton_issues_items = [{'label':hi,'value':hi} for hi in hotbutton_issues]

## get minium requirement 
minium_requirement = list(processor.custom_finder.hot_button_dict.keys())
minium_requirement_items = [{'label':hi,'value':hi} for hi in minium_requirement]

#%%
## load dash style
external_stylesheets = [dbc.themes.BOOTSTRAP,'https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Loading screen CSS
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})

app.config.requests_pathname_prefix = ''
app.config['suppress_callback_exceptions']=True

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
                                 style={'color': '#2c2825','height':'120px'}),
                    ],style={'width':'20%','margin':'10 auto','textAlign': 'center',}),
    
                    html.H3(
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
                    children=html.Div(id='processing_text',children=[
                        'Drag and Drop or ',
                        html.A('Select Files',style={'color':'blue'})
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
                        'opacity':'.5',
                        'margin': 'auto auto 20px auto'
                        },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
    
        ## historical data link
            html.Div(
                children=['For historical timeseries analysis, please visit our ',
                 html.A('Tableau Dashboard', 
                        href='https://tableau.imf.org/#/views/ArticleIVversionchengyu/Country',
                        target='_blank',
                        style={'color':'blue'}
                        )]
                ,style={'textAlign': 'center','margin':'auto'}),
            
        ## hotbutton issues 
            html.Div(children=[
                    html.H5('Hot Button Issues Checklist:',
                            style={'margin': '5px',
                                   'padding':'5px',
                                   }),
                    dcc.Checklist(
                        id='hot-button-issues',
                        options=hotbutton_issues_items,
                        values=[],
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
    
        ## minium requirement
            html.Div(children=[
                    html.H5('Minimum Requirement Checklist:',
                            style={'margin': '5px',
                                   'padding':'5px',
                                   }),
                    dcc.Checklist(
                        id='minimum-requirements',
                        options=minium_requirement_items,
                        values=[],
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
            ## build country dropdown 
            html.Div(id='country-picker',
                     children=[
                        html.Div(
                            children=[   
                                html.Div(' ',style={'width':"20%"}),
                                html.Div('Country Name: ',style={'width':"15%",
                                                                 'textAlign': 'center',
                                                                 'margin-top': 'auto',
                                                                 'margin-bottom':'auto'}),
                                html.Div([            
                                        dcc.Dropdown(
                                            id = 'country-dropdown',
                                            options=country_dropdown_data,
                                            value='United States'
                                        )
                                    ],style={'width':'30%'}),
                                html.Div(' ',style={'width':"20%"}),
                            ],className='row',style={'margin':'auto','padding-top':'30px'})
                        ]
                ,style={'display':'none'}),
    

            ## build the graph object 
            html.Div(id='controls-container2',
                     #children=[dcc.Graph(id='topic-graph')],
                     style={'width':'100%',
                             'display':'block',
                             'padding':'15px',
                             'margin': 'auto'}),
            
            html.Div(id='controls-container',children=[''],style={'display':'block'}),

#            ## build table object
#            html.Div(id='output-data-upload',style={'width': '50%',
#                                                    'margin': 'auto',
#                                                    'padding':'50px'}),
            ## store intemediate data

            html.Div(id='intermediate-value',
                         style={'display': 'none'}),
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
            ## get country name 
            country_name = processor.country_dector.one_step_get_cname(io.BytesIO(decoded))
            ## get hotbutton issues 
            document_for_keywords_check = processor.hot_button_finder.read_doc(io.BytesIO(decoded))
            filtered_hotbutton_issues =processor.hot_button_finder.check_all_topics(document_for_keywords_check)
            filtered_custom_check = processor.custom_finder.check_all_topics(document_for_keywords_check)
            
            ## get topic df
            topic_df = get_topic_df(processor,doc)
            
            ## store json data to div
            data_store = {'doc_name':filename,
                          'country_name':country_name,
                          'doc_date':date,
                          'filtered_hotbutton_issues': filtered_hotbutton_issues,
                          'filtered_custom_check': filtered_custom_check,
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
    try:
        doc,doc_name,doc_date = list_of_contents[0],list_of_names[0],list_of_dates[0]
        res = process_input_data(doc,doc_name,doc_date)
    except:
        res = None
    
    return res    
    
@app.callback(Output('intermediate-value-2', 'children'),
              [Input('intermediate-value', 'children'),
               Input('country-dropdown', 'value')]
              )
def store_historical_dfs(json_data,country_name):
    datasets = json.loads(json_data)
    doc_name = datasets['doc_name']
    doc_date = datasets['doc_date']
    ## load data
    print(country_name)
    #country_name = "Brazil"
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

@app.callback(Output('country-dropdown', 'value'),
              [Input('intermediate-value', 'children')]
              )
def update_country_dropdown(json_data):
    datasets = json.loads(json_data)
    country_name = datasets['country_name']
    return country_name

@app.callback(Output('hot-button-issues', 'values'),
              [Input('intermediate-value', 'children')]
              )
def update_hot_button_issues(json_data):
    datasets = json.loads(json_data)
    issue_names = datasets['filtered_hotbutton_issues']
    return issue_names

@app.callback(Output('minimum-requirements', 'values'),
              [Input('intermediate-value', 'children')]
              )
def update_minimum_requirements(json_data):
    datasets = json.loads(json_data)
    check_names = datasets['filtered_custom_check']
    return check_names

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


@app.callback(Output('country-picker', 'style'), 
              [Input('intermediate-value', 'children')])
def toggle_container1(data):
    if data:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

if __name__ == '__main__':
    #app.run_server(port=8888, host='0.0.0.0', debug=True)
    app.run_server(debug=True)