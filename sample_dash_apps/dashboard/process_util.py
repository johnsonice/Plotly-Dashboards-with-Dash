from gensim import corpora
from gensim.models import LdaModel
import numpy as np
import sys
import os
import gensim
import pickle
import pandas as pd
import datetime
import time
import spacy
from docx import Document
from country_name_util import Country_detector
from hot_button_check_util import Hotbutton_finder,Custom_finder
nlp = spacy.load('en')

class Processor(object):
    """
    an hanlp analyzer object for dependency parsing an other related operations 
    """
    def __init__(self,model_path,dictionary_path,country_map_path,
                 hot_button_file=None,hot_button_dict_path=None,
                 custom_file=None,custom_dict_path=None):
        self.model_path = model_path
        self.dictionary_path = dictionary_path
        self.vocab_dict =  corpora.Dictionary.load(dictionary_path)
        self.model = LdaModel.load(model_path)
        self.country_dector = Country_detector(country_map_path)
        self.hot_button_finder = Hotbutton_finder(hot_button_file,hot_button_dict_path)
        self.custom_finder = Custom_finder(custom_file,custom_dict_path)
        print('LDA model load successfully. ')

    @staticmethod
    def read_doc(f_path,word_length_filter=50):
        doc=Document(f_path)
        text_list=[p.text for p in doc.paragraphs if len(p.text)>word_length_filter]
        return text_list
    
    def get_topics(self,para):
        bow = self.para2bow(para)
        return self.model[bow]
    
    def para2bow(self,paragraph):
        tokens = nlp(paragraph)
        lemmas = [t.lemma_ for t in tokens]
        bow = self.vocab_dict.doc2bow(lemmas)
        return bow
    
    def get_topics_list(self,doc):
        res = [*map(self.get_topics, doc)]
        return res 
    
    def infer_single_paragraph(self,paragraph):
        '''Load raw paragraph and model, return cleaned paragraph and topic_label with highest probability'''
        #### Process text using Spacy for Tokenization/Lemmentization and loaded dictionary for bag-of-words
        new_bow = self.para2bow(paragraph)
        ## Make inference using gensim_lda model (converted from mallet) and retrieve Top ID
        topic_prob = self.model[new_bow]
        n, prob = zip(*topic_prob)
        top_id = np.array(n)[np.array(prob).argmax()]
        top_prob = np.array(prob)[np.array(prob).argmax()]

        return top_id, top_prob
    
    @staticmethod
    def get_id2name_map(id2name_path):
        '''load id 2 name as a dictionary'''
        #map_df = pd.read_csv(id2name_path)
        map_df = pd.read_excel(id2name_path,'Gensim Topic to LdaViz Topic')
        id2name = dict(zip(map_df['Gensim topic id'],map_df['label']))
        return id2name
        
    def get_history():
        return None
    #%%
if __name__ == "__main__":
    ## global folder path 
    model_path = os.path.join('./model_weights/mallet_as_gensim_weights_50_2019_03_08')
    dictionary_path = './model_weights/dictionary.dict'
    country_map_path = './model_weights/country_map.xlsx'
    hot_button_file_path = './model_weights/hot_button_issues.xlsx'
    hot_button_dict_path = './model_weights/hot_button_dict.pickle'
    ## initialize processor
    processor = Processor(model_path,dictionary_path,country_map_path,hot_button_file_path,hot_button_dict_path)
    
    ## try one test file
    text_file_path = "./test/Brazil_2013.DOCX"
    doc = processor.read_doc(text_file_path)
    #%%
    tid,tprob= processor.infer_single_paragraph(doc[0])
    print(tid,tprob)
    #%% 
    ## get country name 
    print(processor.country_dector.one_step_get_cname(text_file_path))
    
    #%%
    ## check hotbutton issues 
    doc_for_hotbutton = processor.hot_button_finder.read_doc(text_file_path)
    print(processor.hot_button_finder.check_all_topics(doc_for_hotbutton))
    
    #%%
#    id2name_path = './model_weights/mapping_file_for_mallet_as_gensim_weights_50_2019_02_12.csv'
#    map_df = pd.read_csv(id2name_path)