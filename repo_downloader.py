import random
import requests as req
from git import Repo

import os

base_url = 'https://api.github.com/'
oldest_request = 1000
max_repo_size = 10000#KB
downloaded_repos_dir = 'downloaded'
temp_repos_dir = 'temp'

#prepare directories
if not os.path.exists(temp_repos_dir):
    os.mkdir(temp_repos_dir)

with open('github_token','r') as f:
    github_api_token = f.readline()


def make_request(request, parameters = dict()):
    parameters['access_token'] = github_api_token
    return req.get(base_url + request, params=parameters).json()

def get_random_repositories_info():
    print(make_request('repos/jakub-tomczak/language-classifier/languages'))

def clone_repo(git_url, repo_dir):
    Repo.clone_from(git_url, repo_dir)

#clones random repository to direcotry [temp_repos_dir]/[page]/
def get_public_repos(page=None):
    pages_cloned = [item for item in os.listdir(os.path.join(temp_repos_dir)) if os.path.isdir(os.path.join(temp_repos_dir, item))]
    print(pages_cloned)
    if page is None:
        page = random.randrange(0, oldest_request)
    while str(page) in pages_cloned:
        page = random.randrange(0, oldest_request)

    print('fetching repos from page %d' % page)
    request = make_request('repositories', parameters={'since':page})
    for data in request:
        try:
            size = make_request('repos/{}/{}'.format(data['owner']['login'], data['name']))['size']
            if size < max_repo_size:
                print('cloning', data['html_url'], data['owner']['login'], data['name'], size, 'as', '{}_{}'.format(data['name'], hash(data['html_url']) ))
                clone_repo(data['html_url'], os.path.join(temp_repos_dir, str(page), '{}_{}'.format(data['name'], hash(data['html_url']) ) ))
        except:
            continue

#fetch random, public 100 repos from github
get_public_repos()
