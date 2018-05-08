import random
import json
import requests as req
from git import Repo
import os

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

get_public_repos()
get_random_repositories_info()