import pandas as pd
from textblob import TextBlob
from tkinter import filedialog
import os

def noun_phrase_gen(text):
    text = TextBlob(text)
    phrases = text.noun_phrases
    return(phrases)

def value_calculator(new_value, average = None, times_occured = None):
    if (average == None):
        return([new_value, 1])
    else:
        value = average * times_occured
        final_value = (value + new_value)/(times_occured + 1)
        return([final_value, times_occured + 1])

def train_data_gen(articles, time_offset = 20, train_data = pd.DataFrame()):
    if train_data.empty:
        train_data = pd.DataFrame({
            'phrase' : "",
            'avg_value' : [0],
            'times_occured' : [0]
        })
    for i in range(len(articles)):
        phrases = noun_phrase_gen(articles.text[i])
        change = articles['Change' + str(time_offset)][i]
        print (i)#For Testing
        for phrase in phrases:
            if any(train_data.phrase.str.match(phrase)):
                ind = train_data.index[train_data.phrase.str.match(phrase).fillna(False)]
                value = value_calculator(change, train_data.avg_value[ind].tolist()[0], train_data.times_occured[ind].tolist()[0])
                train_data.loc[ind, 'avg_value'] = value[0]
                train_data.loc[ind, 'times_occured'] = value[1]
            else:
                value = value_calculator(change)
                train_data = train_data.append({
                    'phrase' : phrase,
                    'avg_value' : value[0],
                    'times_occured' : value[1]
                }, ignore_index = True)
    return(train_data)

article_path = filedialog.askdirectory()
articles = pd.read_csv(article_path + '\\Articles.csv', encoding = 'ISO-8859-1')
save_path = os.getcwd()
#I need to make a button to choose a time_offset value but it's pretty much useless ant takes a lot of time. f you tkinter
time_offset = 60

try:
    train_data = pd.read_csv(save_path + '\\TrainData%s.csv' %time_offset, encoding = 'ISO-8859-1')
except:
    train_data_new = train_data_gen(articles, time_offset=time_offset)
    train_data_new.to_csv(save_path + '\\TrainData%s.csv' %time_offset, index=False, index_label=False)
else:
    train_data_new = train_data_gen(articles, time_offset=time_offset, train_data=train_data)
    train_data_new.to_csv(save_path + '\\TrainData%s.csv' %time_offset, index=False, index_label=False)
