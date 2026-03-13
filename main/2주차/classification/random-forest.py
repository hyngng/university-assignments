import pandas as pd
import numpy as np

path = 'data/diabetes.csv'
# data/breast_cancer.csv도 가능함
# 이 경우 Outcome 대신 label로 명명할 것

df = pd.read_csv(path)

y=df['Outcome']
y.value_counts()

X=df.drop('Outcome',axis=1)
X.head()

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.25,random_state=0)

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

clf_rf = RandomForestClassifier(random_state=0)
clf_rf.fit(X_train, y_train)

pred_rf = clf_rf.predict(X_test)

print ("\n--- Random Forest Classifier ---")
print (accuracy_score(y_test, pred_rf))
print (confusion_matrix(y_test, pred_rf))