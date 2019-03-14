#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 16:08:49 2019

@author: huang
"""


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
nlp = spacy.load('en')
#%%

def get_topics(model,bow):
    return model[bow]

def get_topics_list(model,bows):
    
    res = [*map(lambda x: model.get_document_topics(x), bows)]

    return res 

#%%
    
model_path = os.path.join('mallet_as_gensim_weights_50_2019_03_08')
## gensim dictionrary file 
dictionary_path = os.path.join('dictionary.dict')
## load model 
lda_gensim = LdaModel.load(model_path)
vocab_dict = corpora.Dictionary.load(dictionary_path)
print('Topic Model loaded successfully...')

#%%
text_file_path = "../temp/5138964-v5-Brazil_2013_Article_IV_Consultation_-_Policy_Note.DOCX"

def read_doc(f_path,word_length_filter=50):
    doc=Document(f_path)
    text_list=[p.text for p in doc.paragraphs if len(p.text)>word_length_filter]
    return text_list

 

def infer_single_paragraph(paragraph, ldaModel,vocab_dict):
    '''Load raw paragraph and model, return cleaned paragraph and topic_label with highest probability'''
    #### Process text using Spacy for Tokenization/Lemmentization and loaded dictionary for bag-of-words
    new_text = nlp(paragraph)
    new_doc = [word.lemma_ for word in new_text]
    new_bow = vocab_dict.doc2bow(new_doc)
    
    ## Make inference using gensim_lda model (converted from mallet) and retrieve Top ID
    topic_prob = ldaModel[new_bow]
    n, prob = zip(*topic_prob)
    top_id = np.array(n)[np.array(prob).argmax()]
    
    return new_text, top_id
#%%
res = read_doc(text_file_path)
#%%

text,tid = infer_single_paragraph(res[0],lda_gensim,vocab_dict)
#%%

new_text = nlp(res[0])
new_doc = [word.lemma_ for word in new_text]
new_bow = vocab_dict.doc2bow(new_doc)




