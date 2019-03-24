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
text_file_path = os.path.join(root_path,"dashboard/test/Brazil_2013.DOCX")
historical_data_path = os.path.join(root_path,"dashboard/model_weights/Mallet_50_topics_with_country_year_2019_02_12.xlsx")
id2name_path = os.path.join(root_path,'dashboard/model_weights/mapping_file_for_mallet_as_gensim_weights_50_2019_02_12.csv')