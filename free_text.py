import heapq
import math
import nltk
import pickle

from collections import Counter
from Document import Document
from postings_util import getDocID, getTermWeight, getDocVectorLength

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

def cosineScores(query, dictionary, postingsFile):
    """
    Implementation of CosineScore(q) from the textbook.
    """
    stemmer = nltk.stem.porter.PorterStemmer()
    totalNumberOfDocs = len(retrievePostingsList(postingsFile, dictionary.getPointerToDocLengthsAndTopTerms()))
    result = dict.fromkeys(retrievePostingsList(postingsFile, dictionary.getPointerToDocLengthsAndTopTerms()).keys(), 0) # in the form of {docID : 1, docID2 : 0.2, ...}

    queryTokens = [stemmer.stem(token.lower()) for token in query.split()]
    qTokenFrequency = Counter(queryTokens) # qTokenFrequency will be in the form of {"the": 2, "and" : 1} if the query is "the and the".
    qToken_tfidfWeights = {term : computeTFIDF(term, frequency, dictionary, totalNumberOfDocs) for term, frequency in qTokenFrequency.items()}
    queryLength = math.sqrt(sum([math.pow(weight, 2) for weight in qToken_tfidfWeights.values()]))
    qTokenNormalisedWeights = {term : normaliseWeight(weight,queryLength) for term, weight in qToken_tfidfWeights.items()}
 
    for term in qTokenNormalisedWeights.keys():
        pointer = dictionary.getTermPointer(term)
        postings = retrievePostingsList(postingsFile, pointer) # in the form of (docID, TermFreq, skipPointer (to be discarded))

        for node in postings:
            docID = getDocID(node)
            termWeight = getTermWeight(node)
            docVectorLength = getDocVectorLength(node)
            if docID in result:
                result[docID] += normaliseWeight(qTokenNormalisedWeights[term] * termWeight,  docVectorLength) # update with normalised score
            else:
                result[docID] = normaliseWeight(qTokenNormalisedWeights[term] * termWeight,  docVectorLength)
    
    # documents and their weights are now settled.

    documentObjects = generateDocumentObjects(result)
    output = extractTop10(documentObjects)

    return [document.docID for document in output]

def normaliseWeight(weight, vectorLength):
    """
    Given a weight, divide it by the given vectorLength to normalise.
    """
    if vectorLength == 0: # avoids division by 0
        return 0

    else:
        return weight / vectorLength


def computeTFIDF(term, frequency, dictionary, totalNumberOfDocs):
    """
    Takes in a term and computes the tf-idf of a term.
    """
    df = dictionary.getTermDocFrequency(term)
    if (frequency == 0 or df == 0):
        return 0
    else:
        return (1 + math.log10(frequency)) * math.log10(totalNumberOfDocs/dictionary.getTermDocFrequency(term))


def generateDocumentObjects(result):
    """
    Takes in a dictionary of docID-score pairs and create
    a list of Document objects.
    """
    output = []
    for docID, weight in result.items():
        output.append(Document(docID, weight))

    return output

def extractTop10(documentObjects):
    """
    Takes in a list of Document objects and extracts 10 highest scoring documents.
    Less than 10 Document objects will be outputted if there are documents with score = 0
    amongst the supposed 10 highest.
    """

    temp = heapq.nlargest(10, documentObjects) # a list of 10 highest scoring document

    return filter(lambda document : (document.getWeight() > 0), temp)