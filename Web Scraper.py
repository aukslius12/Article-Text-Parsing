import os
import pandas as pd
import requests
from bs4 import BeautifulSoup

def link_gen(results_path):
    tickers = os.listdir(results_path)
    links = []
    for tick in tickers:
        results = pd.read_csv(results_path + '\\' + tick, encoding = 'ISO-8859-1')
        for link in results['Links'].tolist():
            links.append(link)
    return(links)

def get_texts(urls):
    texts = {
        'url': [],
        'text': []
    }
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

links = link_gen('C:\\Users\\Jurgis\\Desktop\\Automatic-Article-Searcer-V2\\Data\\Results')
#Make this interactive and/or automatically search for files

texts = get_texts(links)
texts = cleanup(texts)
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
    texts = pd.concat([texts,old_texts], ignore_index = True, axis = 0)
    texts.to_csv(dir_path + '\\Articles.csv', index=False, index_label=False)
