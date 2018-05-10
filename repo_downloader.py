import random
import json
import requests as req
from git import Repo
import os
import pandas
import numpy as np
import urllib.request
from bs4 import BeautifulSoup
import urllib.request
import os
import csv

base_url = 'https://api.github.com/'
oldest_request = 1000
max_repo_size = 10000#KB
downloaded_repos_dir = 'downloaded'

def make_request(request, parameters = None):
    return req.get(base_url + request, params=parameters).json()

def get_random_repositories_info():
    print(make_request('repos/jakub-tomczak/language-classifier/languages'))

def clone_repo(git_url, repo_dir):
    Repo.clone_from(git_url, repo_dir)

def get_public_repos(page=None):
    if page == None:
        page = random.randrange(0, oldest_request)
        print('fetching repos from page %d' % page)
    request = make_request('repositories', parameters={'since':page})
    for data in request:
        print(data['html_url'], data['owner']['login'], data['name'])
        size = make_request('repos/{}/{}'.format(data['owner']['login'], data['name']))['size']
        if size < max_repo_size:
            clone_repo(data['html_url'], os.path.join('temp', data['name']))

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
    with open('snippets.csv', 'w', encoding='utf-8') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(['label','text'])
        for root, dirs, files in os.walk(".", topdown=False):
            for name in files:
                for extension in fileExtensionDict.keys():
                    if name.endswith("."+ extension):
                        print(name)
                        with open(os.path.join(root, name), "r", encoding='utf-8') as readfile:
                            try:
                                wr.writerow([extension, readfile.read()])
                            except UnicodeDecodeError:
                                pass
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



#get_public_repos()
get_random_repositories_info()
fileExtensionDict = get_dict_of_top_extensions()
#create_csv_snippets(fileExtensionDict)
read_csv_snippets(fileExtensionDict)