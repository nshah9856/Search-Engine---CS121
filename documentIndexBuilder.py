from bs4 import BeautifulSoup
import os, io
from nltk import word_tokenize
from urllib import urlopen 
import json

rootDir = './WEBPAGES_RAW/'
DOCUMENT_INFO = dict()

def get_website_text(url):
    """
    Getting snippet of text from each webpage
    """
    try:
        response = urlopen(url)
        html = response.read().decode('utf-8')

        soup = BeautifulSoup(html, "html5lib")

        content = soup.find("div")
        
        p = content.find("p")

        paragraph = ["".join(x.findAll(text=True)) for x in p]
        paragraph_body = "%s" % ("".join(paragraph))

        return paragraph_body
        
    except:
        return "No snippet could be collected"

def create_document_index(fileStream, filename):
    """
    Adds the filename as a key and the title of the webpage as its value
    """
    soup = BeautifulSoup(fileStream, "lxml")
    try:
        DOCUMENT_INFO[filename] = {"title": str(soup.title.string).strip()}
    except:
        DOCUMENT_INFO[filename] = {"title": 'No Title'}


def file_traversal():
    """
    Walk down all the files and collect the document index information from each of them
    """
    for dirName, subdirList, fileList in os.walk(rootDir):
        dirNum = dirName[15:]
        for fname in fileList:
            if not fname.startswith('book') and not fname.startswith('.'):
                path = dirName + '/' + fname
                print('reading {}/{}'.format(dirNum, fname))
                with io.open(path, 'r', encoding="utf-8") as fin:
                    create_document_index(fin, dirNum+'/'+fname)

def write_documentInfo_to_file():
    """
    Writing Document index to a file
    """
    with open("Document.txt", "w") as outFile:
        for k,v in DOCUMENT_INFO.items():
            outFile.write("{}:title!{}\n".format(k,v['title']))

if __name__ == "__main__":
    file_traversal()
    write_documentInfo_to_file()
