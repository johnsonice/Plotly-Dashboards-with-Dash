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

class Processor(object):
    """
    an hanlp analyzer object for dependency parsing an other related operations 
    """
    def __init__(self,model_path,dictionary_path):
        self.model_path = model_path
        self.dictionary_path = dictionary_path
        self.vocab_dict =  corpora.Dictionary.load(dictionary_path)
        self.model = LdaModel.load(model_path)
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

    def get_history():
        return None
    
if __name__ == "__main__":
    ## global folder path 
    model_path = os.path.join('./model_weights/mallet_as_gensim_weights_50_2019_03_08')
    dictionary_path = './model_weights/dictionary.dict'
    ## initialize processor
    processor = Processor(model_path,dictionary_path)
    
    ## try one test file
    text_file_path = "../temp/5138964-v5-Brazil_2013_Article_IV_Consultation_-_Policy_Note.DOCX"
    doc = processor.read_doc(text_file_path)
    text,tid,tprob= processor.infer_single_paragraph(doc[0])
    print(text,tid,tprob)
