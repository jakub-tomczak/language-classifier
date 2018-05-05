import requests as req

base_url = 'https://api.github.com/'

def make_request(request, parameters = None):
    return req.get(base_url + request, params=parameters).json()

def get_random_repositories_info():
    print(make_request('repos/jakub-tomczak/language-classifier/languages'))

get_random_repositories_info()