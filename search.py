from xmlrpc.client import boolean
from cv2 import split
import nltk
import sys
import getopt
import pickle
import math
import heapq
from SPIMI import getTermFrequency

from TermDictionary import TermDictionary
from Operand import Operand
from Node import Node
from phrasal import processPharsalQuery
from free_text import cosineScores

TOP_K = 10

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')

    termDict = TermDictionary(dict_file)
    termDict.load()  # load term information into dictFile from dict_file

    with open(queries_file, 'r') as queryFile, open(results_file, 'w') as resultFile:
        allResults = []

        for query in queryFile:
            if query.strip():
                result = processQuery(query, termDict, postings_file)
                if result != None and len(result) > 0:
                    allResults.append(result)

            else:
                allResults.append("")

        outputResult = "\n".join(allResults) # to output all result onto a new line.
        resultFile.write(outputResult)

def isValidQuery(query):
    quotation_count = query.count('\"')
    and_count = query.count('AND')

    if quotation_count % 2 == 1:
        return False
    if quotation_count > 2 and and_count == 0:
        return False
    if quotation_count == 0 and and_count > 1:
        return False
    
    terms = splitQuery(query)
    if len(terms) - and_count > and_count + 1 and and_count >= 1:
        return False

    return True

def processQuery(query, dictFile, postings_file):
    if len(query) == 0 or not isValidQuery(query):
        return

    if "AND" in query:
        return booleanQuery(query, dictFile, postings_file)
    elif '\"' in query:
        return phrasalQuery(query, dictFile, postings_file)
    else:
        return freeTextQuery(query, dictFile, postings_file)


def booleanQuery(query, dictFile, postings_file):
    tokens = shuntingYard(query)
    operants = list()
    while len(tokens) > 0:
        token = tokens.pop()
        if token.isTerm() or token.isResult():
            operants.append(token)
        elif token == 'AND':
            op1 = operants.pop() 
            op2 = operants.pop()
            result = evalAND(op1, op2, dictFile, postings_file)
            operants.append(result)
    return operants.pop()


def freeTextQuery(query, dictFile, postings_file):
    return cosineScores(query, dictFile, postings_file)


def phrasalQuery(query, dictFile, postings_file):
    query = splitQuery(query)[0]
    result = processPharsalQuery(query, dictFile, postings_file)
    return result
    

def shuntingYard(query):
    """
    This is the Shunting-yard algorithm. It parses a query string and returns them
    in Reverse Polish Notation.
    """
    operatorStack = []  # enters from the back, exits from the back
    output = []
    queryTerms = splitQuery(query)

    for term in queryTerms:
        if term == "AND":
            while len(operatorStack) > 0:
                output.append(operatorStack.pop())
            operatorStack.append(term)
        else:
            output.append(term)

    while len(operatorStack) > 0:
        output.append(operatorStack.pop())

    return output


def splitQuery(query):
    """
    Takes in a query string and splits it into an array of query terms and operators,
    without spaces
    """
    temp = nltk.tokenize.word_tokenize(query)
    stemmer = nltk.stem.porter.PorterStemmer()  # stem query like how we stem terms in corpus
    result = []
    flag = 0  # indicates an unclosed apostrophe
    phrase = ""
    
    for term in temp:
        if (term == "\'\'" or term == "\"\"" or term == "``") and flag == 0:
            flag = 1
            continue
        elif (term == "\'\'" or term == "\"\"" or term == "``") and flag == 1:  # phrase concluded
            flag = 0
            result.append(phrase[:len(phrase)-2])  # remove extra space at end of phrase
            phrase = ""
            continue
        elif not term == "AND":  # don't case-fold operators
            if flag == 0:  # not within phrase
                result.append(stemmer.stem(term.lower()))
            else:  # within phrase
                phrase += stemmer.stem(term.lower()) + " "
        else:  # term is an Operator
            result.append(term)
    return result


def retrievePostingsList(file, pointer):
    """
    Given a pointer to determine the location in disk,
    retrieves the postings list from that location.
    """
    if pointer == -1: # for non-existent terms
        return []

    with open(file, 'rb') as f:
        f.seek(pointer)
        postingsList = pickle.load(f)
    f.close()

    return postingsList


def evalAND(operand1, operand2, dictFile, postingsFile):
    """
    input: TermDictionary as dictFile
    input: name of posting file as postingsFile
    output: Operand containing result
    Calls evalAND_terms/evalAND_term_result/evalAND_results depending on operand types
    """
    # Both inputs are terms
    if operand1.isTerm() and operand2.isTerm():
        term1, term2 = operand1.getTerm(), operand2.getTerm()
        result = evalAND_terms(term1, term2, dictFile, postingsFile)

    # Input 1 is term, Input 2 is result
    elif operand1.isTerm() and operand2.isResult():
        term = operand1.getTerm()
        res = operand2.getResult()
        result = evalAND_term_result(term, res, dictFile, postingsFile)

    # Input 2 is term, Input 1 is result
    elif operand2.isTerm() and operand1.isResult():
        term = operand2.getTerm()
        res = operand1.getResult()
        result = evalAND_term_result(term, res, dictFile, postingsFile)

    # Both inputs are results
    else:
        result1 = operand1.getResult()
        result2 = operand2.getResult()
        result = evalAND_results(result1, result2)

    return Operand(term=None, result=result)


def evalAND_terms(term1, term2, dictFile, postingsFile):
    """
    Computes and returns the intersection of the postings lists of the 2 terms provided.
    """
    result = set()
    pointer1 = dictFile.getTermPointer(term1)
    pointer2 = dictFile.getTermPointer(term2)
    pl1 = retrievePostingsList(postingsFile, pointer1)
    pl2 = retrievePostingsList(postingsFile, pointer2)

    if len(pl1) == 0 or len(pl2) == 0:  # either term1 or term2, or both do not exist in the corpus.
        return sorted(result)

    # else, pointer1 and pointer2 are not empty lists

    while pl1 != [] and pl2 != []:
        if Node.getDocID(pl1[0]) == Node.getDocID(pl2[0]):  # Intersection, add to results
            result.add(Node.getDocID(pl1[0]))
            pl1, pl2 = pl1[1:], pl2[1:]
        else:
            # Advance list with smaller docID
            if Node.getDocID(pl1[0]) < Node.getDocID(pl2[0]):
                # Check if skip pointers exist, and use if feasible
                if Node.hasSkip(pl1[0]) and Node.getDocID(pl1[pl1[0].skipPointer]) < Node.getDocID(pl2[0]):
                    pl1 = pl1[pl1[0].skipPointer:]
                else:
                    pl1 = pl1[1:]
            else:
                # Check if skip pointers exist, and use if feasible
                if Node.hasSkip(pl2[0]) and Node.getDocID(pl2[pl2[0].skipPointer]) < Node.getDocID(pl1[0]):
                    pl2 = pl2[pl2[0].skipPointer:]
                else:
                    pl2 = pl2[1:]

    return sorted(result)


def evalAND_term_result(term, res, dictFile, postingsFile):
    """
    Computes and returns the intersection of the postings list of the term and
    result list provided.
    """
    result = set()
    pointer = dictFile.getTermPointer(term)
    pl = retrievePostingsList(postingsFile, pointer)

    if len(pl) == 0 or len(res) == 0:  # if term does not exist in the corpus
        return sorted(result)

    # else, pl and res are not empty lists

    while pl != [] and res != []:
        if Node.getDocID(pl[0]) == res[0]:  # Intersection, add to results
            result.add(res[0])
            pl, res = pl[1:], res[1:]
        else:
            # Advance list with smaller docID
            if Node.getDocID(pl[0]) < res[0]:
                # Check if skip pointers exist, and use if feasible
                if Node.hasSkip(pl[0]) and Node.getDocID(pl[pl[0].skipPointer]) < res[0]:
                    pl = pl[pl[0].skipPointer:]
                else:
                    pl = pl[1:]
            else:
                res = res[1:]

    return sorted(result)


def evalAND_results(result1, result2):
    """
    Computes and returns the intersection of the 2 result list that are provided.
    """
    return sorted(set.intersection(set(result1), set(result2)))


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
