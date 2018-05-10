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
def get_dict_of_extensions():
    numbersOfPages = 4
    fileExtensionDict = {}
    mapIndex = 0
    for page in range(numbersOfPages):
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
#get_public_repos()
get_random_repositories_info()
fileExtensionDict = get_dict_of_extensions()
some_problems_here(fileExtensionDict)