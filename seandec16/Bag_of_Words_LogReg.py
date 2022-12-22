#!/usr/bin/env python
# coding: utf-8


from random import shuffle
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from pandas import DataFrame
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score


def normalize_features(X_train, X_test):
    from sklearn.preprocessing import StandardScaler # import library 
    scaler = StandardScaler() # call an object function
    scaler.fit(X_train)   # calculate mean, std in X_train  (x-u)/s
    X_train_norm = scaler.transform(X_train)  # apply normalization on X_train
    X_test_norm = scaler.transform(X_test)    # apply normalization on X_test
    return X_train_norm, X_test_norm


def load_seeds(filename="seeds.txt"):
    seeds = []
    with open(filename, "r") as s: #load seed words
        for seed in s:
            seed_word = seed.strip()
            seeds.append(seed_word)
    return seeds

def load_text_file_as_list(filename: str):
    lines = []
    with open(filename, "r") as f: #load text
        for line in f:
            text = line.replace("\n", "")
            lines.append(text)
    return lines 

def load_text_file_as_list_of_dictionaries(filename: str = "causal_text.csv"):
    out = []
    for text in load_text_file_as_list(filename=filename):
        out.append({"text": text})
    return out

def load_data(text_filename:str = "causal_text.csv",
              seeds_filename: str = "seeds.txt") -> DataFrame:  

    seeds = load_seeds(seeds_filename)
    lines = load_text_file_as_list_of_dictionaries(text_filename)
                
    df = pd.DataFrame(lines)

    label = []
    for row in df['text']:
        if any(word in row for word in seeds): #assign labels based on seed words
            label.append(1)
        else:
            label.append(0)
            
    df["labels"] = label

    return df

def load_training_data_revised(seeds_file="seeds.txt", filename="all_data.txt"):
    '''shorter sentences are better?'''

    all_ = load_text_file_as_list(filename)
    all_ = [o for o in all_ if len(o.split(' ')) < 50]
    shuffle(all_)

    seeds = load_seeds(seeds_file)

    yes = [o for o in all_ if any(i in o for i in seeds)][0:2000]
    no = [o for o in all_ if not any(i in o for i in seeds)][0:2000]
    out = [{"text": i, "labels": 1} for i in yes]
    out = out + [{"text": i, "labels": 0} for i in no]
    return yes, no, pd.DataFrame(out)

#yesses = load_text_file_as_list("yes.txt")
#nos = load_text_file_as_list("no.txt")
yesses, nos, df = load_training_data_revised()

#split into input and label data for training
X = df.text
y = df.labels

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(X) # create bag of words

LogReg = LogisticRegression()
LogReg.fit(X, y)

# examine coefficients
coef = LogReg.coef_[0]
feats = vectorizer.get_feature_names_out()
l = pd.DataFrame([{"coef": c, "feat": f} for c, f in zip(coef, feats)])
l.sort_values("coef", ascending=False)[0:200]


runtime = pd.DataFrame(load_text_file_as_list_of_dictionaries('all_data.txt'))
X_run = vectorizer.transform(runtime["text"])
runtime["prob"] = LogReg.predict_proba(X_run)[:,1]
runtime = runtime.sort_values("prob", ascending=False)
runtime = runtime.to_dict(orient='records')

# limiting to short sentences seems to really help a lot in annotating these
# also the shorter sentences contain fewer anaphora and so are better in our setting
runtime = [i for i in runtime if i["text"] not in yesses and i["text"] not in nos and len(i["text"].split()) < 50]
runtime = pd.DataFrame(runtime)
runtime = runtime[0:100]
runtime.to_csv("tmp.csv")