import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tkinter import messagebox, filedialog

def raw_or_not():
    result = messagebox.askyesno('', 'Would you like to get raw article text?')
    texts = get_texts(links)
    if result == False:
        texts = cleanup(texts)
        return (texts)
    else:
        return(pd.DataFrame.from_dict(texts))

def link_gen(results_path):
    tickers = os.listdir(results_path)
    links = []
    for tick in tickers:
        results = pd.read_csv(results_path + '\\' + tick, encoding = 'ISO-8859-1')
        for link in results['Links'].tolist():
            links.append(link)
    return(links)

def value_gen(results_path, offset):
    tickers = os.listdir(results_path)
    value = []
    for tick in tickers:
        results = pd.read_csv(results_path + '\\' + tick, encoding = 'ISO-8859-1')
        last0 = results['Last0'].tolist()
        value_name = 'Last' + str(offset)
        last_offset = results[value_name].tolist()
        for i in range(len(last0)):
            value.append((last_offset[i] - last0[i]) / last0[i] * 100)
    return(value)

def get_values(texts, results_path):
    texts['Change20'] = value_gen(results_path, offset=20)
    texts['Change60'] = value_gen(results_path, offset=60)
    texts['Change120'] = value_gen(results_path, offset=120)
    return(texts)

def get_texts(urls):
    texts = {
        'url': [],
        'text': []
    }
    i = 1 #For Testing
    for url in urls:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        tags = soup.find_all('p')
        text = []
        for tag in tags:
            text.append(tag.get_text())
        text = ' '.join(text)
        texts['url'].append(url)
        texts['text'].append(text)
        print (i) #For Testing
        i = i + 1  #For Testing
    return(texts)

def cleanup(texts):
    clean_texts = {
        'url' : texts['url'],
        'text' : []
    }
    for text in texts['text']:
        text = text.split()
        temp_text = []
        for word in text:
            temp_text.append(''.join(e for e in word if e.isalnum() and not e.isdigit()))
        temp_text = [t for t in temp_text if t]
        text = ' '.join(temp_text)
        text = text.lower()
        clean_texts['text'].append(text)
    return(pd.DataFrame.from_dict(clean_texts))

def text_missing(texts):
    missing = []
    for i in range(len(texts.text)):
        if '' == texts.text[i]:
            missing.append(texts.url[i])
    return(missing)

results_path = filedialog.askdirectory()
links = link_gen(results_path)
texts = raw_or_not()
texts = get_values(texts, results_path)
text_missing(texts)
#This could be included inside cleanup function, but I need to figure out the causes for this issue.
#For example wsj needs you to subscribe to view their articles.
for missing_value in text_missing(texts):
    texts = texts[texts.url != missing_value]

dir_path = os.getcwd()
try:
    old_texts = pd.read_csv(dir_path + '\\Articles.csv', encoding = 'ISO-8859-1')
except:
    texts.to_csv(dir_path + '\\Articles.csv', index=False, index_label=False)
else:
    texts = pd.concat([old_texts, texts], ignore_index = True, axis = 0)
    texts.to_csv(dir_path + '\\Articles.csv', index=False, index_label=False)

