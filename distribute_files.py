import pickle
from multiprocessing import Process, freeze_support
import os

import shutil

from classifier import get_dict_of_top_extensions
from shutil import copy, move


threads_num = 8
root_dir = 'temp'
file_list_dump = 'dump_file_list_temp_languages'
files_dict = dict()
languages_types = [ 'typescript', 'cpp','kotlin', 'latex', 'pascal', 'objectiveC', 'swift', 'scala', 'r', 'go', 'xml']

def get_files_list(dir, files_dict):
    list = os.listdir(dir)
    if not list:
        shutil.rmtree(dir)
        return
    for node in list:
        joined = os.path.join(dir, node)
        if os.path.isfile(joined):
            extension = node.split('.')[-1]
            if extension in files_dict:     #this file has not been indexed yet
                files_dict[extension].append( joined )
            else:
                os.remove(joined)
        elif os.path.isdir(joined):
            if node == '.git':
                shutil.rmtree(joined, ignore_errors=True)
            else:
                get_files_list(joined, files_dict)

def remove_empty_extensions(extensions):
    new_extensions = dict()
    for extension in extensions.keys():
        if len(extensions[extension]) > 0:
            new_extensions[extension] = extensions[extension]
    return new_extensions

def copy_to_proper_dir(list, files_dict):
    print('copying', ' '.join(list))
    for extension in list :
        for file in files_dict[extension]:
            copy(file, os.path.join(os.path.curdir, 'datasets', 'out', extension))

#prepare extensions list
def init_prepare():
    global files_dict
    extensions = get_dict_of_top_extensions()
    for extension in extensions:
        path = os.path.join('datasets', 'out', extension)
        if(not os.path.exists(path)):
            os.mkdir(os.path.join('datasets', 'out', extension))
    for extension in extensions.keys():
        files_dict[extension] = []

def get_summary(files_dict):
    language_stats = dict()
    for extension in files_dict.keys():
        language_stats[extension] = len(files_dict[extension])

    from functools import reduce
    sum = reduce(lambda x, y : x+y, map(lambda x: len(x), files_dict.values()))
    return (language_stats, sum)

def load_files():
    print('getting files list...')
    global files_dict

    if os.path.exists(file_list_dump):
        with open(file_list_dump, 'rb') as file:
            files_dict = pickle.load(file)
    else:
        get_files_list(root_dir, files_dict)

    #dump files list
    with open(file_list_dump, 'wb') as file:
        pickle.dump(files_dict, file)

    print('completed')

def move_first_1000_files(languages, dir, counters, deep):
    global counter_limit
    global how_deep
    list = os.listdir(dir)
    if not list:
        shutil.rmtree(dir)
        return (counters, deep - 1)
    for node in list:
        joined = os.path.join(dir, node)
        if os.path.isfile(joined):
            extension = node.split('.')[-1]
            #check if current file extension is taken into account
            if extension in languages:
                if counters[extension] >= counter_limit:
                    continue
                dst_file = os.path.join('1000_files', '{}'.format(extension), node)
                if(not os.path.exists(dst_file)):
                    counters[extension] += 1
                    copy(joined, dst_file)
        elif os.path.isdir(joined):
            #remove git files
            if node == '.git':
                shutil.rmtree(joined, ignore_errors=True)
            else:
                if(deep > how_deep):
                    return (counters, deep-1)
                deep+=1
                (counters, deep) = move_first_1000_files(languages, joined, counters, deep)
    return (counters, deep - 1)

#copies files from prepared dict that contains paths to files with specified language
def copy_using_dict(language, counter, files_dict):
    global counter_limit
    copied = 0
    for file in files_dict[language]:
        filename = file.split('\\')
        if len(filename) < 1:
            continue
        filename = filename[-1]
        dst_file = os.path.join('1000_files', '{}'.format(language), filename)
        if(not os.path.exists(file)):
            #files_dict may be outdated
            continue
        if (not os.path.exists(dst_file)):
            if counter < counter_limit:
                counter += 1
                copied += 1
                copy(file, dst_file)
    print('copied files for language' , language, ' ', copied)
top_languages = get_dict_of_top_extensions()

counter_limit = 1000
how_deep = 15
if __name__=='__main__':

    files_dict = dict()
    counters = dict()

    for extension in top_languages.keys():
        #initialize counters
        counters[extension] = 0
        files_dict[extension] = []

    #load dict with files paths
    load_files()
    for key, value in top_languages.items():
        path = '1000_files/{}'.format(key)
        if(not os.path.exists(path)):
            os.mkdir(path)
        counters[key] = len( os.listdir(path) )
        print('language', value, 'files already', counters[key], 'to copy', counter_limit - counters[key] )
        if (counter_limit - counters[key] <= 0):
            print('language', value,'files already copied(files -', counters[key], ')' )

    languages_extensions = top_languages.keys()
    #copy files using reccurent root traversing
    #move_first_1000_files(languages_extensions, 'temp', counters, 0)

    #copy files using prepared dict
    for key, value in top_languages.items():
        copy_using_dict(key, counters[key], files_dict)
'''
    #print stats
    list, sum = get_summary(files_dict)
    for item in list.keys():
        print('{};{}'.format(item, list[item]))
    print('suma;{}'.format(sum) )
'''
    #copies files with extensions using 8 process
    #copy_parallel()


