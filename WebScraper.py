import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tkinter import messagebox, filedialog

def raw_or_not(info):
    result = messagebox.askyesno('', 'Would you like to get raw article text?')
    texts = get_texts(info)
    if result == False:
        texts = cleanup(texts)
        return (texts)
    else:
        return(pd.DataFrame.from_dict(texts))

def info_gen(results_path):
    tickers = os.listdir(results_path)
    links = []
    headlines = []
    for tick in tickers:
        results = pd.read_csv(results_path + '\\' + tick, encoding = 'ISO-8859-1')
        for link in results['Links'].tolist():
            links.append(link)
        for headline in results['Headlines'].tolist():
            headlines.append(headline)
    return({'Links': links,
           'Headlines': headlines})

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

def get_texts(info):
    texts = {
        'headline': [],
        'text': [],
        'par': []
    }
    i = 1 #For Testing
    for i in range(len(info['Links'])):
        page = requests.get(info['Links'][i])
        soup = BeautifulSoup(page.content, 'html.parser')
        tags = soup.find_all('p')
        text = []
        for tag in tags:
            text.append(tag.get_text())
        texts['headline'].append(info['Headlines'][i])
        texts['text'].append(text)
        texts['par'].append(len(tags))
        print (i) #For Testing
    return(texts)

def cleanup(texts):
    clean_texts = {
        'url' : texts['url'],
        'text' : [],
        'par': texts['par']
    }
    for text in texts['text']:
        text = text.split()
        temp_text = []
        for word in text:
            temp_text.append(''.join(e for e in word if e.isalnum() and not e.isdigit()))
        temp_text = [t for t in temp_text if t]
        text = text.lower()
        clean_texts['text'].append(text)
    return(pd.DataFrame.from_dict(clean_texts))

def text_missing(texts):
    missing = []
    for i in range(len(texts.text)):
        if '' == texts.text[i]:
            missing.append(texts.url[i])
    return(missing)


def split_files(texts):
    headline_file = texts.drop('text', axis=1)
    headline_file = headline_file.drop('par', axis=1)
    text_file = {
        'paragraph': [],
        'par_no': [],
        'Change20': [],
        'Change60': [],
        'Change120': []
    }
    for i in range(len(texts['text'])):
        j = 1
        for text in texts['text'][i]:
            text_file['paragraph'].append(text)
            text_file['par_no'].append(j)
            j = j + 1
            text_file['Change20'].append(texts['Change20'][i])
            text_file['Change60'].append(texts['Change20'][i])
            text_file['Change120'].append(texts['Change20'][i])

    return ([pd.DataFrame.from_dict(headline_file), pd.DataFrame.from_dict(text_file)])

results_path = filedialog.askdirectory()
info = info_gen(results_path)
texts = raw_or_not(info)
texts = get_values(texts, results_path)
text_missing(texts)
#This could be included inside cleanup function, but I need to figure out the causes for this issue.
#For example wsj needs you to subscribe to view their articles.
for missing_value in text_missing(texts):
    texts = texts[texts.url != missing_value]

texts = split_files(texts)

dir_path = os.getcwd()
try:
    old_headlines = pd.read_csv(dir_path + '\\Headlines.csv', encoding = 'ISO-8859-1')
    old_texts = pd.read_csv(dir_path + '\\Texts.csv', encoding='ISO-8859-1')
except:
    texts[0].to_csv(dir_path + '\\Headlines.csv', index=False, index_label=False)
    texts[1].to_csv(dir_path + '\\Texts.csv', index=False, index_label=False)
else:
    texts[0] = pd.concat([old_headlines, texts[0]], ignore_index = True, axis = 0)
    texts[1] = pd.concat([old_texts, texts[1]], ignore_index=True, axis=0)
    texts[0].to_csv(dir_path + '\\Headlines.csv', index=False, index_label=False)
    texts[0].to_csv(dir_path + '\\Texts.csv', index=False, index_label=False)
