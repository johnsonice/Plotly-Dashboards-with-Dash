#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 09:48:59 2019

@author: huang
"""

import pandas as pd
#import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.offline as pyo
import sys
from process_util import Processor
from evaluate import get_topic_df
import copy
import os
#%%
def aggregate_doc_topic_distribution(df):
    df['para_length'] = df['text'].apply(lambda x: len(x.split()))
    df['content_size_old'] = df['para_length']*df['probability']
    df = df.groupby(['country','gensim_topic','year'])['content_size_old'].sum()
    return df


def get_county_df(agg_df,country_name,year):
    country_df = pd.DataFrame(agg_df.loc[country_name,:,year])
    country_df.reset_index(inplace=True)  
    return country_df
    
def get_top_topic_ids(country_df,topic_df,topn=5):
    test_df = pd.merge(country_df,topic_df,how='right',on='gensim_topic')
    test_df['df'] = test_df['content_size'] - test_df['content_size_old']
    test_df.sort_values(by=['df'],inplace=True,ascending=False) 
    top_topic_ids = test_df.head(topn)['gensim_topic'].tolist()
    return top_topic_ids

def get_plot_df_list(topic_ids,df_agg,topic_df,country):
    ts_dfs = []
    for i in topic_ids:
        df_i = pd.DataFrame(df_agg.loc[country,i,:]).reset_index()
        new_value = topic_df['content_size'][topic_df['gensim_topic']==i].tolist()[0]
        df_i = df_i.append({'gensim_topic':i,'year':'current','content_size_old':new_value},ignore_index=True)
        ts_dfs.append(df_i)
    return ts_dfs

def get_plot_data(df_agg,country,doc_path,processor,topn=4):

    ## get lattest year for that country
    temp = df_agg.loc[country,:].reset_index()
    lattest_year = temp['year'].unique()[-1]
    country_df = get_county_df(df_agg,country,lattest_year)
    
    ## process doc 
    doc = processor.read_doc(doc_path)
    topic_df = get_topic_df(processor,doc)
    
    ## get ts dfs
    topic_ids = get_top_topic_ids(country_df,topic_df,topn)
    ts_dfs = get_plot_df_list(topic_ids,df_agg,topic_df,country)
    
    return ts_dfs

def create_graph(df,xaxis_name,yaxis_name):
    df = copy.copy(df)
    topic_name = str(df['gensim_topic'].iloc[0])
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

    
#%%
    
if __name__ == "__main__":

    #sentiment_path = '../model_weights/sentiment_analysis_2019_02_12.xlsx'
    topic_path = 'model_weights/Mallet_50_topics_with_country_year_2019_04_10.xlsx'
    hot_button_file_path = os.path.join('./model_weights/hot_button_issues.xlsx')
    hot_button_dict_path = os.path.join('./model_weights/hot_button_dict.pickle')
    
    processor = Processor('model_weights/mallet_as_gensim_weights_50_2019_03_08',
                          'model_weights/dictionary.dict',
                          './model_weights/country_map.xlsx',
                          hot_button_file_path,
                          hot_button_dict_path)

    data_df = pd.read_excel(topic_path,'Document and Topic')
    df_agg = aggregate_doc_topic_distribution(data_df)
    #%%
    ## print out country names
    print(df_agg.index.get_level_values(0).unique())
    ts_dfs= get_plot_data(df_agg,"Brazil",'./test/Brazil_2013.DOCX',processor,6)
    #ts_dfs
    #%%
    res = {}
    for idx,d in enumerate(ts_dfs):
        d.plot.bar(x='year',y='content_size_old')
        res['df_'+str(idx)] = d.to_json(orient='split', date_format='iso')
        
    ## try create one graph
    #%%
    fig_data = create_graph(ts_dfs[0],'year','content_size_old')
    pyo.plot(fig_data,filename='test/test2.html')
    
    #%%
#    data_df = pd.read_excel(topic_path,'Document and Topic')
#    #%%
#    df_agg = aggregate_doc_topic_distribution(data_df)
#    
#    us_df = get_county_df(df_agg,"United States",2018)
#    
#    processor = Processor('../model_weights/mallet_as_gensim_weights_50_2019_03_08',
#                          '../model_weights/dictionary.dict')
#    
#    ## process doc 
#    doc = processor.read_doc('Brazil_2013.DOCX')
#    topic_df = get_topic_df(processor,doc)
#    
#    #%%
#    topic_ids = get_top_topic_ids(us_df,topic_df,4)
#    ts_dfs = get_plot_df_list(topic_ids,df_agg,topic_df,'United States')
#    
#    #%%
#    ts_dfs[3].plot.bar(x='year',y='content_size_old')
