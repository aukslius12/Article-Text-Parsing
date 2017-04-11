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

def redirected_urls(urls):
    rurls = []
    failed_urls = []
    for url in urls:
        try:
            page = requests.get(url).content
        except:
            failed_urls.append(url)
        else:
            soup = BeautifulSoup(page, 'lxml')
            element = soup.find('meta', attrs={'http-equiv': 'refresh'})
            try:
                refresh_content = element['content']
            except:
                rurls.append(url)
            else:
                rurls.append(refresh_content.partition('=')[2][1:-1])
    if len(failed_urls) == 0:
        return({'Redirected Urls' : rurls})
    else:
        return({'Redirected Urls' : rurls, 'Failed Urls' : failed_urls})

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

raw_links = link_gen('C:\\Users\\Jurgis\\Desktop\\Automatic-Article-Searcer-V2\\Data\\Results')
#Make this interactive and/or automatically search for files

links = redirected_urls(raw_links)
#print(links['Failed Urls'])
#Failed urls should be relevant. Maybe if it exceeds some sort of treshold it should print a warning?

texts = get_texts(links['Redirected Urls'])


