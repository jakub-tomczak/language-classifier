import random
import json
import requests as req
import os

base_url = 'https://api.github.com/'
oldest_request = 1000
downloaded_repos_dir = 'downloaded'

def make_request(request, parameters = None):
    return req.get(base_url + request, params=parameters).json()

def get_random_repositories_info():
    print(make_request('repos/jakub-tomczak/language-classifier/languages'))

def get_public_repos(page=None):
    if page == None:
        page = random.randrange(0, oldest_request)
        print('fetching repos from page %d' % page)
    request = make_request('repositories', parameters={'since':page})
    for data in request:
        print(data['html_url'])
get_public_repos()
get_random_repositories_info()