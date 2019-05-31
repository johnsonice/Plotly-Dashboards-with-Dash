#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 21:34:11 2019

@author: huang
"""
import os 

root_path = '.'
model_path = os.path.join(root_path,'dashboard/model_weights/mallet_as_gensim_weights_50_2019_03_08')
dictionary_path = os.path.join(root_path,'dashboard/model_weights/dictionary.dict')



## most likely you will only need to change these two path 
#historical_data_path = os.path.join(root_path,"dashboard/model_weights/Mallet_50_topics_with_country_year_2019_02_12.xlsx")
historical_data_path = os.path.join(root_path,"dashboard/model_weights/Mallet_50_topics_with_country_year_2019_04_10.xlsx")
#id2name_path = os.path.join(root_path,'dashboard/model_weights/mapping_file_for_mallet_as_gensim_weights_50_2019_02_12.csv')
id2name_path = os.path.join(root_path,"dashboard/model_weights/Mallet_50_topics_with_country_year_2019_04_10.xlsx")

## if historical data has been updated, need to delete the cashed pkl file in order to refresh new data 
df_agg_pkl_path = os.path.join(root_path,'dashboard/model_weights/df_agg.pkl')

country_map_path = os.path.join(root_path,'dashboard/model_weights/country_map.xlsx')


## keywords check input files 
hot_button_file_path = os.path.join(root_path,'dashboard/model_weights/keywords_search/hot_button_issues.xlsx')
hot_button_dict_path = os.path.join(root_path,'dashboard/model_weights/keywords_search/hot_button_dict.pickle')

adhoc_check_file_path = os.path.join(root_path,'dashboard/model_weights/keywords_search/minimum_requirement.xlsx')
adhoc_check_dict_path = os.path.join(root_path,'dashboard/model_weights/keywords_search/custom_dict.pickle')



text_file_path = os.path.join(root_path,"dashboard/test/Brazil_2013.DOCX")