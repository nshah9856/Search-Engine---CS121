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

    # with open("QueryResults.txt", "a") as dataFile:
    #     print "Total Number of Documents : ", TOTAL_DOCUMENTS
    #     dataFile.write("Total Number of Documents : {}".format(TOTAL_DOCUMENTS))
        # while True:
            # print
            # s = raw_input("Enter the query: ")
            # for s in search.split():
            #     GLOBAL_INDEX[s]



        # print "Searching..", s
        # output = []
        # print "\nTop 20 results\n"
        # dataFile.write("\nQuery : {}\n".format(s))
        results = 0


        #Cosine Similarity Method
        query_vector = []

        modified_query = []
        
        for i in s.split():
            if not i.isupper():
                modified_query.append(i.lower())
            else:
                modified_query.append(i)

        tf = Counter(modified_query)

        results = defaultdict(float)

        for query in modified_query:  
            try:                
                df = math.log(TOTAL_DOCUMENTS / len(GLOBAL_INDEX[query]))
                wtq = (1 + math.log(tf[query])) * df
                query_vector.append(wtq)
            except:
                query_vector.append(0)
                

        doc_dictionary = defaultdict(list)

        for query in modified_query:
            for d in GLOBAL_INDEX[query]:
                doc_dictionary[d['DocID']].append(float(d['TFIDF']))


        for k,v in doc_dictionary.items():

            results[k] = 1 - spatial.distance.cosine(query_vector, v)

                # document_vector = []
                # document_vector.append(int(d['TFIDF']))
                # # print query_vector, document_vector
                # rank_result = spatial.distance.cosine(query_vector, document_vector)
                # results[d['DocID']] += rank_result
        

        top20 = sorted(results, key=lambda x: x[1], reverse=True)[:20]

        # print top20
        output = []
        for i in top20:
            link = data[i]
            if not link.startswith('http'):
                link = "http://" + link
            
            output.append((link,DOCUMENT_INFO[i]))
        return output
        # return [(data[i],DOCUMENT_INFO[i]) for i in top20]

        # print results
        # for d in GLOBAL_INDEX[s]:
        #     results += 1
        #     if results <= 20:
        #         output.append(data[d['DocID']])
                # print "{}. {} \nTF-IDF Score: {}".format(results, data[d['DocID']], d['TFIDF'])
                # dataFile.write("{}. {}\n".format(results,data[d['DocID']]))
            # else:
                # dataFile.write("{}. {}\n".format(results,data[d['DocID']]))

        # print "\nTotal Results found : ", results
        # dataFile.write("Total Results found : {}\n".format(results))
        # return output


app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('my-form.html')

@app.route('/result',methods = ['POST', 'GET'])
def my_form_post():
    text = request.form['text']
    queryResults = query(text.strip())
    return render_template('result.html',result = queryResults)
    # s = ""
    # for link, data in queryResults:
    #     if str(link).startswith('http'):
    #         s += "<p><a target=\"_blank\" href={}>{}</a></p>".format(link, data['title'])
    #     else:
    #         s += "<p><a target=\"_blank\" href={}>{}</a></p>".format("http://" + link,data['title'])

    # return s

if __name__ == '__main__':
    buildIndexFromFile("Index.txt")
    buildDocumentIndexFromFile("Document.txt")
    # print DOCUMENT_INFO['61/160']
    # query("computer science")
    app.run()
