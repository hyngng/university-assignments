# 2026-03-13 수업 중 실습
# 회귀로 worst compactness에 대해 평균제곱근오차 구하기

import pandas as pd
import numpy as np

path = '/content/drive/MyDrive/Colab Notebooks/breast_cancer.csv'

df  = pd.read_csv(path)

df2 = df.drop('label',axis=1)
df.head()

y = df2['worst compactness']
y.value_counts()

X = df2.drop('worst compactness',axis=1)
X.head()

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.25,random_state=0)

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

model = LinearRegression()
model.fit(X_train, y_train)
ly_preds = model.predict(X_test)

print('평균제곱근오차', mean_squared_error(ly_preds, y_test))

def mse_np(actual, predicted):
    return np.mean((np.array(actual) - np.array(predicted)) ** 2)

print('평균제곱근오차', mse_np(ly_preds, y_test))

def mse(actual, predicted):
    sum_square_error = sum((a - p) ** 2 for a, p in zip(actual, predicted))
    mean_square_error = sum_square_error / len(actual)
    return mean_square_error

print('평균제곱근오차', mse(ly_preds, y_test))