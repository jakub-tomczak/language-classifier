from classifier import *

fileExtensionDict = dict()

#create test and training sets from available data
def create_datasets():
    fileExtensionDict = get_dict_of_top_extensions()
    create_csv_snippets(fileExtensionDict)


#execute snippet classification
def classify():
    read_csv_snippets(fileExtensionDict)

if __name__=='__main__':
    create_datasets()
    classify()