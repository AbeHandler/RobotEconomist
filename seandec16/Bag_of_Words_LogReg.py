#!/usr/bin/env python
# coding: utf-8

# In[109]:


import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score


# In[110]:


def normalize_features(X_train, X_test):
    from sklearn.preprocessing import StandardScaler # import library 
    scaler = StandardScaler() # call an object function
    scaler.fit(X_train)   # calculate mean, std in X_train  (x-u)/s
    X_train_norm = scaler.transform(X_train)  # apply normalization on X_train
    X_test_norm = scaler.transform(X_test)    # apply normalization on X_test
    return X_train_norm, X_test_norm


# In[111]:


#load concatenated yes and no data in csv format

lines = []
seeds = []
label = []
with open("seeds.txt", "r") as s: #load seed words
    for seed in s:
        seed_word = seed.strip()
        seeds.append(seed_word)

with open("causal_text.csv", "r") as f: #load text
    for line in f:
        text = line
        lines.append({"text": text})
            
df = pd.DataFrame(lines)

for row in df['text']:
    if any(word in row for word in seeds): #assign labels based on seed words
        label.append(1)
    else:
        label.append(0)
        
df["labels"] = label

#split into input and label data for training

X = df.text
y = df.labels

df.head()


# In[112]:


vectorizer = CountVectorizer()
X = vectorizer.fit_transform(X) #create bag of words

X_train, X_test, y_train, y_test = train_test_split(X, y) #split data for testing 

#X_train_norm, X_test_norm = normalize_features(X_train, X_test)


# In[113]:


#summary of words in data

feature_names = vectorizer.get_feature_names()
print("Number of features: {}".format(len(feature_names)))
print("Last 15 Features: {}".format(feature_names[(2857-15):2857]))
#vectorizer.vocabulary_


# In[114]:


#performance metrics 

LogReg = LogisticRegression()
LogReg.fit(X_train, y_train)

CV_scores = cross_val_score(LogReg, X_train, y_train, cv = 5)
print("Cross Validation Mean Score: {}".format(np.mean(CV_scores)))

print("Training Score: {}".format(LogReg.score(X_train, y_train)))
print("Testing Score: {}".format(LogReg.score(X_test, y_test)))


# In[115]:


#confusion matrix for false negatives and positives

y_pred = LogReg.predict(X_test)
confusion = confusion_matrix(y_test, y_pred)

print("Confusion Matrix: {}".format(confusion))


# In[116]:


#Examine predicted probabilities vs class labels

probabilities = LogReg.predict_proba(X_test)

probabilities = np.delete(probabilities, 0, axis=1)

y_prob = []
for i in range(probabilities.shape[0]):
    y_prob.append(np.around(probabilities[i],2))
    
y_prob = np.array(y_prob).ravel()

MSE = np.mean((np.array(y_test) - np.array(y_prob))**2)
print("Mean Squared Error: {}".format(MSE))


# In[ ]:




