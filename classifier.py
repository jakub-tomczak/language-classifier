import csv
from sklearn.feature_extraction.text import CountVectorizer
import operator
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import os
import pandas
import numpy as np
import urllib.request
from bs4 import BeautifulSoup
import urllib.request

# create a dictionary: key- file extension,
# value is a list of index (for mapping) and list of possible descriptions (programming languages)
def get_dict_of_all_extensions():
    numberOfPages = 4
    fileExtensionDict = {}
    mapIndex = 0
    for page in range(numberOfPages):
        with urllib.request.urlopen('https://www.file-extensions.org/filetype/extension/name/source-code-and-script-files/sortBy/visits/order/desc/page/' + str(page+1)) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            data = soup.find_all('td')[2:]
            for extensionString, description in zip(data[0::2], data[1::2]):
                extension = extensionString.getText()[16:]
                if extension in fileExtensionDict:
                    fileExtensionDict[extension][1].append(description.getText())
                else:
                    fileExtensionDict[extension] = [mapIndex, [description.getText()]]
                    mapIndex += 1

    print(fileExtensionDict['cpp']) #example display
    return fileExtensionDict

# there are some file extensions referring to many different programming languages :/
def some_problems_here(fileExtensionDict):
    for x in fileExtensionDict:
        if len(fileExtensionDict[x][1]) > 1:
            print(x + ": " +str(fileExtensionDict[x]))
# create a dict containing only TOP languages
def get_dict_of_top_extensions():
    fileExtensionDict = {}
    with open("topProgrammingLanguagesExtensions.txt", "r") as readfile:
        for line in readfile:
            data = line.strip('\n').split(' ')
            fileExtensionDict[data[0]] = data[1]
    print(fileExtensionDict['cpp']) #example display
    return fileExtensionDict


def create_csv_snippets(fileExtensionDict):
    countExtension = {x: 0 for x in fileExtensionDict.keys()}
    with open('snippets.csv', 'w', encoding='utf-8') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(['label','text'])
        for root, dirs, files in os.walk(".", topdown=False):
            for name in files:
                for extension in fileExtensionDict.keys():
                    if name.endswith("."+ extension) and countExtension[extension] < 120\
                            and os.path.getsize(os.path.join(root, name)) < 20480: # size < 20kB
                        #print(os.path.getsize(os.path.join(root, name)))
                        countExtension[extension] += 1
                        with open(os.path.join(root, name), "r", encoding='utf-8') as readfile:
                            try:
                                wr.writerow([extension, readfile.read()])
                            except UnicodeDecodeError:
                                countExtension[extension] -= 1
                                #pass


def get_top_occuring_words(X_train_counts, how_many_words, vectorizer, train):
    id_to_word = {v: k for k, v in vectorizer.vocabulary_.items()} # stwórz mapowanie pozycji wektora bag-of-words na konkretne słowa
    cx = X_train_counts.tocoo()

    category_word_counts = dict()      # słownik, w którym przeprowadzimy zliczanie

    for doc_id, word_id, count in zip(cx.row, cx.col, cx.data):
        category = train.iloc[doc_id]['label']  # w category znajduje się idetyfikator kategorii dla aktualnego dokumentu, zapisujemy go
        word = id_to_word[word_id]              # w word - aktualne słowo z dokumentu
                                                # mamy też liczność wystąpienia danego słowa w dokumencie (gdzie? :) )

        if category not in category_word_counts.keys(): # stwórzmy słownik z kategoriami jako kluczami
            category_word_counts[category] = dict()     # jeśli widzimy nową kategorię - dodajemy do słownika

        if word not in category_word_counts[category]: # w ramach każdej kategorii będziemy zliaczać słowa
            category_word_counts[category][word] = 0.0 # jeśli aktualne słowo jeszce nie zotało uwzględnione w kategorii - zainicjujmy jego licznik liczbą 0

        category_word_counts[category][word] += count

    for category_name in category_word_counts.keys(): # wyświetl nazwy kategorii i n najczęściej występujących w nich słów
        sorted_cat = sorted(category_word_counts[category_name].items(), key=operator.itemgetter(1), reverse=True) # posortowany dict() słowo -> liczność, wg liczności, malejąco
        print("{cat}: {top}".format(cat=category_name, top=[word for word, count in sorted_cat[:how_many_words]])) # wyświetl nazwę kategorii i top n słów


def read_csv_snippets(fileExtensionDict):
    full_dataset = pandas.read_csv('snippets.csv', encoding='utf-8')
    myMap = {}
    index = 0
    for elem in fileExtensionDict.keys():
        myMap[elem] = index
        index += 1
    full_dataset['label_num'] = full_dataset.label.map(myMap) #map labels to int to enable classification
    print(full_dataset.head()) # show data sample

    np.random.seed(0) #set seed to 0 to enable reproducible experiment
    train_indices = np.random.rand(len(full_dataset)) < 0.7 # get random 70% of data for training set
    train = full_dataset[train_indices] # training set (70%)
    test = full_dataset[~train_indices] # test set (30%)

    print("Number of elements in training set: {train}, test: {test}".format(
        train=len(train), test=len(test)
    ))

    print("\n\nClass count in training set: ")
    print(train.label.value_counts())

    print("\n\nClass count in test set: ")
    print(test.label.value_counts())


    vectorizer = CountVectorizer(encoding=u'utf-8', max_features=10000)
    X_train_counts = vectorizer.fit_transform(train['text'].values.astype('U')) # stwórz macierz liczbową z danych.
    # W wierszach mamy kolejne dokumenty, w kolumnach kolejne pola wektora cech odpowiadające unikalnym słowom (bag of words)
    X_test_counts = vectorizer.transform(test['text'].values.astype('U'))
    # analogicznie jak wyżej - dla zbioru testowego.

    print("Rozmiar stworzonej macierzy: {x}".format(x=X_train_counts.shape))
    # wyświetl rozmiar macierzy. Pierwsze pole - liczba dokumentów, drugie - liczba cech (stała dla wszystkich dokumentów)
    print("Liczba dokumentów: {x}".format(x=X_train_counts.shape[0]))
    print("Rozmiar wektora bag-of-words {x}".format(x=X_train_counts.shape[1]))

    print("Rozmiar stworzonej macierzy: {x}".format(x=X_test_counts.shape))
    get_top_occuring_words(X_train_counts, 12, vectorizer, train) # wywołanie funkcji


    nb = MultinomialNB() # STWÓRZ KLASYFIKATOR
    nb.fit(X_train_counts, train['label_num']) # WYTRENUJ KLASYFIKATOR
    accuracy = nb.score(X_test_counts, test['label_num']) # OBLICZ TRAFNOŚĆ
    print(accuracy)
    print("Szczegółowy raport (per klasa)")
    print(classification_report(test['label_num'], (nb.predict(X_test_counts)))) # testowanie klasyfikatora - szerokie podsumowanie uwzględniające miary: precision, recall, f1



def get_count_extensions(fileExtensionDict):
    countExtension = {x: 0 for x in fileExtensionDict.keys()}
    for root, dirs, files in os.walk("1000_files", topdown=False):
        for name in files:
            for extension in fileExtensionDict.keys():
                if name.endswith("."+ extension):
                    countExtension[extension] += 1
    print(countExtension)
    return countExtension