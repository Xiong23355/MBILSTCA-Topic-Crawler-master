# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 15:57:50 2023

@author: Xiong
"""

import gensim,jieba

def cut_sentence(text):
    stop_list = [line[:-1] for line in open("./resources/中文停用词表.txt",encoding='gb18030', errors='ignore')]
    result = []
    for each in text:
        each_cut = jieba.cut(each)
        each_split = ' '.join(each_cut).split()
        each_result = [word for word in each_split if word not in stop_list] #去除停用词
        result.append(' '.join(each_result))
    return result

def caculate_relavance(data,model_dm):
    test_text = cut_sentence(data)[0].split(' ')
    inferred_vector = model_dm.infer_vector(doc_words=test_text)
    sims = model_dm.dv.most_similar([inferred_vector],topn=10)
    relavance = sum(float(sim[1]) for sim in sims)/10
    return relavance

    