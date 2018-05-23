'''
repo_downloader.py uses github api to get list of public repositories
that sizes are under max_repo_size size. When a repo's url is resolved and size is
lower that max_repo_size then it starts cloning it to the temp_repos_dir directory.
More info https://developer.github.com/v3/ .
If you have a github token (without it you can clone less repos)
paste it to the file named github_token . This file is in gitignore list so your token
will stay safe.
'''
import random
import requests as req
from git import Repo

import os

base_url = 'https://api.github.com/'
oldest_request = 1000
max_repo_size = 20000#KB !0MB
downloaded_repos_dir = 'downloaded'
temp_repos_dir = 'temp_languages'

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

#clones random repository to direcotry [temp_repos_dir]/[page]/[repoName_hash(repoName)]
#hash of repoName is needed since there may be planty of repos with identical names
def get_public_repos(page=None, parameters=dict(), url=None, dest_dir = None):
    if dest_dir is None:
        pages_cloned = [item for item in os.listdir(os.path.join(temp_repos_dir)) if os.path.isdir(os.path.join(temp_repos_dir, item))]
        print(pages_cloned)
        if page is None:
            page = random.randrange(0, oldest_request)
        while str(page) in pages_cloned:
            page = random.randrange(0, oldest_request)

        print('fetching repos from page %d' % page)
        parameters['since'] = page

    parameters['per_page'] = 30
    #parameters['page'] = 3
    request = make_request( 'repositories' if url is None else url, parameters=parameters)
    print('parameters', parameters)
    #for data in request:
    for data in request['items']:
        try:
            #print('repo with language', parameters['q'], data['html_url'])
            size = make_request('repos/{}/{}'.format(data['owner']['login'], data['name']))['size']
            if size < max_repo_size:
                print('cloning', data['html_url'], data['owner']['login'], data['name'], size, 'as', '{}_{}'.format(data['name'], hash(data['html_url']) ))
                clone_repo(data['html_url'], os.path.join(temp_repos_dir, str(page) if dest_dir is None else dest_dir, '{}'.format(data['name']))) # hash(data['html_url'])
        except Exception as e:
            print(e)

language = 'csharp'
# 'typescript','kotlin', ,'latex', 'pascal', 'objectiveC', 'swift', 'scala', 'r', 'go', 'cpp', 'xml'
languages_types = ['typescript']
for language in languages_types:
    get_public_repos(parameters={'q' : 'language:{}'.format(language)}, url = 'search/repositories', dest_dir = language)