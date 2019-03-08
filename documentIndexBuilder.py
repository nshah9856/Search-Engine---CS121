from bs4 import BeautifulSoup
import os, io
from nltk import word_tokenize
from urllib import urlopen 
import json


rootDir = './WEBPAGES_RAW/'
DOCUMENT_INFO = dict()

def get_website_text(url, div_class=0, _return=0):
    #Get HTML from URL
    try:
        response = urlopen(url)
        html = response.read().decode('utf-8')

        soup = BeautifulSoup(html, "html5lib")

        content = soup.find("div")
        
        #Parser Content Error Message
        # if len(str(content)) < 1000:
        #     print ("Your request may not be returning the desired results.", '\n' \
        #                 "Consider inspecting the webpage and trying a different div tag", '\n')
        #     print ("CURRENT RESULTS:", '\n', content)
        # else:
        #     pass
        

        #Get Paragraph Body
        p = content.find("p")

        # if content != None:
        #     paragraph = []
        #     count = 0
        #     for x in content.find("p"):
        #         count += 1
        #         if count == 3:
        #             break
        #         paragraph.append("".join(x.findAll(text=True)))

        paragraph = ["".join(x.findAll(text=True)) for x in p]
        paragraph_body = "%s" % ("".join(paragraph))

            
            #Return Function Option
            # if _return==1:
        return paragraph_body
            # else:
            #     print (paragraph_body)
        #     pass
        # else:
        #     return "No snippet could be collected"

    except:
        return "No snippet could be collected"

def create_document_index(fileStream, filename):
    # data = None
    # with open(rootDir + 'bookkeeping.json') as book:
    #     data = json.load(book)
    #     print get_website_text("http://" + data[filename])

    soup = BeautifulSoup(fileStream, "lxml")
    # print get_summary(fileStream)
    try:
        DOCUMENT_INFO[filename] = {"title": str(soup.title.string).strip()}
    except:
        DOCUMENT_INFO[filename] = {"title": 'No Title'}


def file_traversal():
    # count = 0
    for dirName, subdirList, fileList in os.walk(rootDir):
        dirNum = dirName[15:]
        for fname in fileList:
            if not fname.startswith('book') and not fname.startswith('.'):
                # count += 1
                path = dirName + '/' + fname
                print('reading {}/{}'.format(dirNum, fname))
                with io.open(path, 'r', encoding="utf-8") as fin:
                    # if count == 100:
                        # return
                    create_document_index(fin, dirNum+'/'+fname)

def write_documentInfo_to_file():
    with open("Document.txt", "w") as outFile:
        for k,v in DOCUMENT_INFO.items():
            outFile.write("{}:title!{}\n".format(k,v['title']))
        #     for i in v:
        #         outFile.write( "DocID-{},TokenFreq-{},TFIDF-{}:".format(i.docID, i.tokenFrequency, i.tfidf))
        #     outFile.write("\n")

if __name__ == "__main__":
    file_traversal()
    write_documentInfo_to_file()
