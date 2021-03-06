
# -*- coding: UTF-8 -*-
import pandas as pd
from tkinter import *
import tkinter as tk
import nltk
import arabic_reshaper
import matplotlib.pyplot as plt 
import re
from sklearn.decomposition import PCA
from gensim.models import Word2Vec
from nltk.stem.isri import ISRIStemmer
from bidi.algorithm import get_display
from wordcloud import WordCloud

# Download Arabic stop words
nltk.download('stopwords')

# Extract Arabic stop words
arb_stopwords = set(nltk.corpus.stopwords.words("arabic"))

# Initialize Arabic stemmer
st = ISRIStemmer()

# Load Quran from csv into a dataframe
df = pd.read_csv('data/arabic-original.csv', sep='|', header='infer');

# Remove harakat from the verses to simplify the corpus
df['verse'] = df['verse'].map(lambda x: re.sub('[ًٌٍَُِّۙ~ْۖۗ]', '', x))
                
# Tokinize words from verses and vectorize them
df['verse'] = df['verse'].str.split()

# Remove Arabic stop words
df['verse'] = df['verse'].map(lambda x: [w for w in x if w not in arb_stopwords])

# Exclude these words from the stemmer
stem_not = ['الله', 'لله', 'إلهكم', 'اله', 'لله', 'إلهكم', 'إله', 'بالله', 'ولله']

# [On/Off] Stemming the words to reduce dimensionality except stem_not list
# df['verse'] = df['verse'].map(lambda x: [w if w in stem_not else st.stem(w) for w in x])

# You can filter for one surah too if you want!
verses = df['verse'].values.tolist()

# train model
model = Word2Vec(verses, min_count=15, window=7, workers=8, alpha=0.22)
# summarize the loaded model

# fit a 2d PCA model to the vectors
X = model[model.wv.vocab]
pca = PCA(n_components=2)
result = pca.fit_transform(X)
# create a scatter plot of the projection
plt.scatter(result[:, 0], result[:, 1])
words = list(model.wv.vocab)

# Pass list of words as an argument
# disable for now in order to show the one below
# for i, word in enumerate(words):
   # reshaped_text = arabic_reshaper.reshape(word)
   # artext = get_display(reshaped_text)
   # plt.annotate(artext, xy=(result[i, 0], result[i, 1]))
   # plt.show()

def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform
    
    return platforms[sys.platform]


def print_word_cloud_ar(artext_list):
    """Takes a list of Arabic words to print cloud."""
    full_string = ' '.join(artext_list)
    reshaped_text = arabic_reshaper.reshape(full_string)
    artext = get_display(reshaped_text)
    
    # Build the Arabic word cloud
    # use KacstOne font for linux systems because the other fonts cause errors
    if get_platform() == "linux":
        wordc = WordCloud(font_path='KacstOne',background_color='white',width=2000,height=1000).generate(artext)
    else:
        wordc = WordCloud(font_path='tahoma',background_color='white',width=2000,height=1000).generate(artext)
    # Draw the word cloud
    plt.imshow(wordc) 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 
    
    plt.show()
    
    
def print_similar_word_cloud(one_word, topn):
    """Takes an Arabic word and print similar word cloud for top number of words {$topn}."""
    temp_list=model.wv.most_similar(positive=[one_word], negative=[], topn=topn)
    similar_words=[i[0] for i in temp_list]
    print_word_cloud_ar(similar_words)

# simple gui but arabic is reversed in text box not a problem after clicking button
root = tk.Tk()
User_input = Entry()
User_input.pack()

def func(event):
    print_similar_word_cloud(User_input.get(),50)

root.bind('<Return>', func)

def onclick():
    print_similar_word_cloud(User_input.get(),50)

reshaped_text2 = arabic_reshaper.reshape("أدخل الكلمة التي تريد البحث عنها")
artext2 = get_display(reshaped_text2)
button = tk.Button(root, text=artext2, command=onclick)
button.pack()

root.mainloop()
