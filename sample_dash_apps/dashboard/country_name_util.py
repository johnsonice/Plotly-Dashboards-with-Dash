#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 09:37:28 2019

@author: huang
"""

## country name detect module 

from docx import Document
import pandas as pd

#%%

class Country_detector(object):
    """
    recognize countries in a given context 
    """
    def __init__(self,country_map_path):
        self.country_map_path = country_map_path
        self.country2id, self.id2country = self.read_country_map(country_map_path)
        
        print('country map read successfully.')
        
    @staticmethod
    def read_context(doc_path,word_length_filter=5):
        doc = Document(doc_path)
        text_list=[p.text for p in doc.paragraphs if len(p.text)>word_length_filter]
        country_context = ' '.join(text_list[:6]).lower()
        
        return country_context 
    
    @staticmethod
    def read_country_map(map_path):
        id2country_df = pd.read_excel(map_path,'id2country',header=None)
        id2country = dict(zip(id2country_df[0],id2country_df[1]))
        country2id_df = pd.read_excel(map_path,'country2id',header=None)
        country2id = dict(zip(country2id_df[0],country2id_df[1]))
        
        return country2id,id2country
    
    @staticmethod
    def check_country_string(c_name,context):
        c_name = c_name.lower().replace(","," ")
        c_list = c_name.split()
        check_list = [c in context for c in c_list]
        res = all(check_list)
        return res
    
    
    def extract_country(self,country_context,default_country='United States'):
        for c_name,v in self.country2id.items():
            country_check = self.check_country_string(c_name,country_context)
            if country_check:
                res_country_name = self.id2country[self.country2id[c_name]]
                return res_country_name
        
        print('No country name matched, return United States as default.')
        return default_country 

    def one_step_get_cname(self,doc_path):
        '''
        one step function to call to get country name
        '''
        context = self.read_context(doc_path)
        c_res = self.extract_country(context)
        
        return c_res
        
#%%
if __name__=="__main__":
    doc_path = 'Brazil_2013.DOCX'
    country_map_path = 'country_map.xlsx'
    
    c_detector = Country_detector(country_map_path)

    #context = 'test has gong through dractic changes in the past 5 years'
    c = c_detector.one_step_get_cname(doc_path)
    print(c)
