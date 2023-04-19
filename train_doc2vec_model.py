# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 15:34:17 2023

@author: Xiong
"""

import jieba
import gensim

TaggededDocument=gensim.models.doc2vec.TaggedDocument

def cut_sentence(text):
    stop_list = [line[:-1] for line in open("./resources/中文停用词表.txt",encoding='gb18030', errors='ignore')]
    result = []
    for each in text:
        each_cut = jieba.cut(each)
        each_split = ' '.join(each_cut).split()
        each_result = [word for word in each_split if word not in stop_list] #去除停用词
        result.append(' '.join(each_result))
    return result

def readtxt(filename):
    comments=[]
    with open(filename,'r',encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip('\n')
            if len(line)>10:
                comments.append(line)
        f.close()
    return comments


def X_train(cut_sentence):
    x_train = []
    for i, text in enumerate(cut_sentence):
        word_list = text.split(' ')
        l = len(word_list)
        word_list[l-1] = word_list[l-1].strip()
        document = TaggededDocument(word_list,tags=[i])
        x_train.append(document)
    return x_train

def train(x_train):
    model = gensim.models.doc2vec.Doc2Vec(x_train,min_count=1,window=3,vector_size=300,sample=1e-3,negative=5,workers=4)
    model.train(x_train,total_examples=model.corpus_count,epochs=10)
    return model
   
def main(corpus):
    data=readtxt(corpus)#语料库
    cut_data=cut_sentence(data)
    train_data=X_train(cut_data)
    model_dm = train(train_data)
    return model_dm
    
    
    
    
    
    