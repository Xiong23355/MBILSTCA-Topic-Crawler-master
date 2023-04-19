# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 10:43:50 2023

@author: Xiong
"""

from sklearn.neural_network import MLPRegressor
from sklearn import model_selection
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import numpy as np
import joblib

def ones_fit(data):
    x=np.array([i[0:8] for i in data])
    y=np.array([i[-2:] for i in data])
    X_train, X_test, y_train, y_test = model_selection.train_test_split(x, y, test_size=0.2)
    
    model_mlp = MLPRegressor(
        hidden_layer_sizes=(8,), activation='relu', solver='sgd', alpha=0.0001, batch_size='auto',
        learning_rate='constant', learning_rate_init=0.001, power_t=0.5, max_iter=5000, shuffle=True,
        random_state=1, tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True,
        early_stopping=False,beta_1=0.9, beta_2=0.999, epsilon=1e-08)
    model_mlp.fit(X_train, y_train)
    expected=y_test
    predicted = model_mlp.predict(X_test)
    mse = mean_squared_error(expected, predicted)/10
    r2 = r2_score(expected, predicted)
    print('MSE:',str(mse),'\n','R2:',str(r2))
    joblib.dump(model_mlp,'model.dat')
    
def part_fit(model_file,data):
    try:
        model_mlp = joblib.load('model.dat')
        x=np.array([i[0:8] for i in data])
        y=np.array([i[-2:] for i in data])
        X_train, X_test, y_train, y_test = model_selection.train_test_split(x, y, test_size=0.5)
        model_mlp.partial_fit(x,y)
        expected=y_test
        predicted = model_mlp.predict(X_test)
        mse = mean_squared_error(expected, predicted)/10
        r2 = r2_score(expected, predicted)
        print('MSE:',str(mse),'\n','R2:',str(r2))
        joblib.dump(model_mlp,'model.dat')
        
    except:
        print('No available model')
        
def acceptance_caculate(model_file,data):
    try:
        model_mlp = joblib.load('model.dat')
        predicted = model_mlp.predict(data)
        print('Radical:',predicted[0],'\n','Conservative:',predicted[1])
        return predicted[0],predicted[1]
    except:
        print('No available model or Wrong data')
        return 0,0
    