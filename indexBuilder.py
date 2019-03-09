from nltk import word_tokenize, pos_tag, Text, sent_tokenize
from nltk.probability import FreqDist
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import math
import os, io
from collections import defaultdict
import json
from bs4 import BeautifulSoup
from bs4.element import Comment


#GLOBAL DEFINITIONS 

rootDir = './WEBPAGES_RAW/'
GLOBAL_INDEX = defaultdict(list)

class Data:
    """
    Data object to make it easier to add a new Posting in the Posting list for each term/token.
    """
    def __init__(self):
        self.docID = None
        self.tokenFrequency = None
        self.tfidf = None

def visible_tags(element):
    """
    Returns true for tags that are considered to be visible to the user, and false otherwise.
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def normalize(fileStream, filename): #Normalizing
    """
    This function normalizes the tokens by removing punctuations, adding case insensitivity(mostly), and removing stop words. 
    The function then adds those 'good' tokens to the global index with its corresponding Data object.
    """
    soup = BeautifulSoup(fileStream, "lxml")
    token = []
    everything = soup.find_all(text=True)
    visible_texts = filter(visible_tags, everything)

    for line in visible_texts:
        tokenizer = RegexpTokenizer(r'[a-zA-Z][a-zA-Z0-9]+')     #Remove the punctuations - we dont want to store punctuation as tokens
        tokens = tokenizer.tokenize(line)
        stop_words = stopwords.words('english')

        for i in tokens:
            if i not in stop_words and i not in {'br', 'nbsp', 'body', 'html', 'li', 'p', 'span', 'href'}: #Removing stop words
                if i.isupper(): 
                    token.append(i) #dont lowercase it if the whole word is all uppercase
                else:
                    token.append(i.lower()) #case insensitivity
    
    freq = FreqDist(token)
    
    for i in set(token):
        d = Data()
        d.docID = filename
        d.tokenFrequency = freq[i]
        GLOBAL_INDEX[i].append(d)


def print_global_index():
    """
        Printing the global index to the terminal
    """
    for k,v in GLOBAL_INDEX.items():
        print "Token : ", k, " -> ", 
        for i in v:
            print "DocID: ", i.docID, " TokenFreq: ", i.tokenFrequency,
        print

def generate_index():
    """
        This function walks the directories and files and calls on normalize function to build the index.
    """
    TOTAL_DOCUMENTS = 0 
    for dirName, subdirList, fileList in os.walk(rootDir):
        dirNum = dirName[15:]
        for fname in fileList:
            if not fname.startswith('book') and not fname.startswith('.'):
                path = dirName + '/' + fname
                # if "61/354" == dirNum+'/'+fname:
                print('reading {}/{}'.format(dirNum, fname))
                with io.open(path, 'r', encoding="utf-8") as fin:
                    TOTAL_DOCUMENTS += 1
                    normalize(fin, dirNum+'/'+fname)

    return TOTAL_DOCUMENTS

def modify_index(TOTAL_DOCUMENTS): #Adding the tfidf to the Index
    """
    After the initial index is built, this function adds the tfidf's for each document
    """
    for k,v in GLOBAL_INDEX.items():
        dck = len(v)
        for i in v:
            i.tfidf = math.fabs((1 + math.log(i.tokenFrequency)) * math.log(TOTAL_DOCUMENTS/dck))

def write_index_to_file(TOTAL_DOCUMENTS): #Writing index to a file! AND gathering data
    """
    This function writes out the data to a file names "Index.text"
    """
    INDEX_COUNT = 0
    with open("Index.txt", "w") as outFile:
        outFile.write("TOTAL_DOCUMENTS: {}\n".format(TOTAL_DOCUMENTS))
        for k,v in GLOBAL_INDEX.items():
            INDEX_COUNT += 1
            outFile.write("Token:{}:".format(k))
            for i in v:
                outFile.write( "DocID-{},TokenFreq-{},TFIDF-{}:".format(i.docID, i.tokenFrequency, i.tfidf))
            outFile.write("\n")
        # outFile.write("\n Total Number of Tokens: {} ".format(INDEX_COUNT))


if __name__ == "__main__":
    TOTAL_DOCUMENTS = generate_index()
    modify_index(TOTAL_DOCUMENTS)
    write_index_to_file(TOTAL_DOCUMENTS)
