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
    texts = {'url': [], 'text': []}
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

links = link_gen('C:\\Users\\Jurgis\\Desktop\\Automatic-Article-Searcer-V2\\Data\\Results')
#Make this interactive and/or automatically search for files

texts = get_texts(links)


