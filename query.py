from collections import defaultdict
import json
from flask import Flask, request, render_template
from collections import Counter
import math
from scipy import spatial

#GLOBAL DEFINITIONS
GLOBAL_INDEX = defaultdict(list)
rootDir = './WEBPAGES_RAW/'
TOTAL_DOCUMENTS = 0
DOCUMENT_INFO = dict()

def buildIndexFromFile(filename):
    """
    This function read in from the Index.txt and builds the Index so that the queries can be generated super fast.
    """
    global TOTAL_DOCUMENTS
    with open(filename, "r") as inFile:
        TOTAL_DOCUMENTS = int(inFile.readline().strip().split()[1])

        for line in inFile.readlines():
            line = line.strip().split(':')
            token = line[1]
            for i in line[2:]:
                d = dict()
                for j in i.split(','):
                    k = j.split('-')
                    if len(k) == 2:
                        d[k[0]] = k[1]
                
                if (len(d) != 0):
                    GLOBAL_INDEX[token].append(d)
    # return TOTAL_DOCUMENTS

def buildDocumentIndexFromFile(filename):
    with open(filename) as inFile:
        for line in inFile.readlines():
            line = line.strip().split(':')
            for i in line[1:]:
                d = dict()
                for j in i.split(','):
                    k = j.split('!')
                    if len(k) == 2:
                        d[k[0]] = k[1]
                
                if (len(d) != 0):
                    DOCUMENT_INFO[line[0]] = d

    # for k,v in DOCUMENT_INFO.items():
    #     print k,v
            
def query(s):
    """
    This function takes in a query and applies the consine similarity method to find and rank the best top20 results.
    """
    data = None
    with open(rootDir + 'bookkeeping.json') as book:
        data = json.load(book)

        #Cosine Similarity Method
        query_vector = []

        modified_query = []
        
        for i in s.split():
            if not i.isupper():
                modified_query.append(i.lower())
            else:
                modified_query.append(i)

        tf = Counter(modified_query)

        Scores = defaultdict(float)
        Magnitude = defaultdict(float)

        for query in modified_query:  

            query_tfidf = (1 + math.log(tf[query])) * math.log(TOTAL_DOCUMENTS/len(GLOBAL_INDEX[query]))

            for document in GLOBAL_INDEX[query]:
                Scores[document['DocID']] += query_tfidf * float(document['TFIDF'])
                Magnitude[document['DocID']] += float(document['TFIDF']) ** 2

        result = defaultdict(float)
        for doc in Scores:
            result[doc] = Scores[doc] / math.sqrt(Magnitude[doc])


        top20 = sorted(result.items(), key=lambda x: x[1], reverse=True)[:20]
        top20 = [k for k,v in top20]

        output = []
        for i in top20:
            link = data[i]
            if not link.startswith('http'):
                link = "http://" + link
            
            output.append((link,DOCUMENT_INFO[i]))
        return output

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('my-form.html')

@app.route('/result',methods = ['POST', 'GET'])
def my_form_post():
    text = request.form['text']
    queryResults = query(text.strip())
    return render_template('result.html',result = queryResults)

if __name__ == '__main__':
    buildIndexFromFile("Index.txt")
    buildDocumentIndexFromFile("Document.txt")
    app.run()
