import base64
import datetime
import io
import plotly.graph_objs as go
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from docx import Document
import pandas as pd

import os
import sys
sys.path.insert(0,'./dashboard')
from process_util import Processor
from evaluate import get_topic_df
import config
#%%
## initialize processor
processor = Processor(config.model_path,config.dictionary_path)

## load dash style
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.requests_pathname_prefix = ''


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

elements = [
            html.H2(
                children='SPR Review Document Topic Analysis',
                style={
                    'textAlign': 'center',
                    'padding': '50px',
                    #'color': colors['text']
                }
            ),
            dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                        ]),
                    style={
                        'width': '100%',
                        'height': '80px',
                        'lineHeight': '80px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                        },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
            ## build the graph object 
            dcc.Graph(id='topic-graph'),
            ## build table object
            html.Div(id='output-data-upload',style={'width': '50%',
                                                    'margin': 'auto',
                                                    'padding':'50px'}),
        ]

app.layout = html.Div(elements)

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
            
#                    # For debugging, display the raw contents provided by the web browser
#                    html.Div('Raw Content'),
#                    html.Pre(contents[0:200] + '...', style={
#                        'whiteSpace': 'pre-wrap',
#                        'wordBreak': 'break-all'
#                    })
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

def create_graph(df,xaxis_name,yaxis_name):
    df[xaxis_name]=df[xaxis_name].apply(lambda x: "Topic-"+str(x))
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
    res = create_graph(topic_df,'gensim_topic','content_size') 
    return res
    
#%%
#@app.callback(Output('output-data-upload', 'children'),
#              [Input('upload-data', 'contents')],
#              [State('upload-data', 'filename'),
#               State('upload-data', 'last_modified')])
#def update_output(list_of_contents, list_of_names, list_of_dates):
#    if list_of_contents is not None:
#        children = [
#            #parse_contents(c, n, d) for c, n, d in
#            parse_doc(c, n, d) for c, n, d in
#            zip(list_of_contents, list_of_names, list_of_dates)]
#        return children

#%%
@app.callback(Output('topic-graph', 'figure'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output_graph(list_of_contents, list_of_names, list_of_dates):
    children = None
    if list_of_contents is not None:
        children = [
            #parse_contents(c, n, d) for c, n, d in
            update_graph(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
    if len(children) > 0:
        children = children[0]
    return children

    

if __name__ == '__main__':
    #app.run_server(port=8888, host='0.0.0.0', debug=True)
    app.run_server(debug=True)