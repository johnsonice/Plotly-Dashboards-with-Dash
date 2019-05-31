#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 21:39:59 2019

@author: huang
"""

import os
from process_util import Processor
#import config
import pandas as pd
#import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.offline as pyo

#%%
def merge_transform_topic_df(topic_model_res,df_doc):
    
    doc_topic_df = pd.DataFrame(topic_model_res)
    doc_topic_df['paragraph_id'] = doc_topic_df.index.to_list()
    
    #reshape from wide to long
    doc_topic_df  = doc_topic_df.melt(id_vars='paragraph_id')
    doc_topic_df = doc_topic_df[doc_topic_df['value'].notnull()]
    doc_topic_df['gensim_topic'] = doc_topic_df['value'].apply(lambda x: x[0])
    doc_topic_df['probability'] = doc_topic_df['value'].apply(lambda x: x[1])
    doc_topic_df  = doc_topic_df[['paragraph_id','gensim_topic', 'probability']]
    
    ## merge database
    doc_topic_full_df = pd.merge(df_doc,doc_topic_df,left_index=True,right_on=['paragraph_id'])
     
    return doc_topic_full_df

def aggregate_doc_topic_distribution(df):
    df['para_length'] = df['text'].apply(lambda x: len(x.split()))  
    df['content_size'] = df['para_length']*df['probability']
    df_res = df.groupby('gensim_topic').content_size.agg('sum')
    return df_res

def get_topic_df(processor,doc):
    df_doc = pd.DataFrame(doc,columns=['text'])
    topic_res = processor.get_topics_list(doc)
    doc_topic_full_df = merge_transform_topic_df(topic_res,df_doc)
    df_res = aggregate_doc_topic_distribution(doc_topic_full_df)
    df_res = df_res.to_frame()
    df_res.reset_index(level=0, inplace=True)
    df_res.sort_values(by='content_size', ascending=False,inplace=True)
    return df_res

def create_graph(df,xaxis_name,yaxis_name):
    
#    df[xaxis_name]=df[xaxis_name].astype(str)
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

#%%
if __name__ == "__main__":
    ## initialize processor
    processor = Processor('model_weights/mallet_as_gensim_weights_50_2019_03_08',
                          'model_weights/dictionary.dict')
    
    ## process doc 
    doc = processor.read_doc('test/Brazil_2013.DOCX')
    topic_df = get_topic_df(processor,doc)
    topic_df['content_size'].plot(kind='bar')
    #plotly chart
    fig_data = create_graph(topic_df,'gensim_topic','content_size')
    pyo.plot(fig_data,filename='test/test.html')
    
    
    
    
    