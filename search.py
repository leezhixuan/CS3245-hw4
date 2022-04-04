from xmlrpc.client import boolean
import nltk
import sys
import getopt
import pickle
import math
import heapq

from TermDictionary import TermDictionary


def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    dictFile = TermDictionary(dict_file)
    dictFile.load()  # load term information into dictFile from dict_file

    with open(queries_file, 'r') as queryFile, open(results_file, 'w') as resultFile:
        allResults = []

        for query in queryFile:
            if query.strip():
                result = processQuery(query, dictFile, postings_file)
                allResults.append(result)

            else:
                allResults.append("")

        outputResult = "\n".join(allResults) # to output all result onto a new line.
        resultFile.write(outputResult)

def processQuery(query):
    if len(query) == 0:
        return

    if "AND" in query:
        booleanQuery(query)
    else:
        pass


def booleanQuery(query):
    pass

def freeTextQuery(query):
    pass

def phrasalQuery(query):
    pass


    


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
