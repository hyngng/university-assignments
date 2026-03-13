# 2026-03-13 수업 중 실습

import pandas as pd
import numpy as np

path = '/content/drive/MyDrive/Colab Notebooks/breast_cancer.csv'

df = pd.read_csv(path)

y=df['label']
y.value_counts()

X=df.drop('label',axis=1)
X.head()

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.25,random_state=0)

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

clf_lr = LogisticRegression(random_state=0)
clf_lr.fit(X_train, y_train)

pred_lr = clf_lr.predict(X_test)

print ("\n--- Logistic Regression Classifier ---")
print (accuracy_score(y_test, pred_lr))
print (confusion_matrix(y_test, pred_lr))