#!/usr/bin/python3
import csv
import string
import shutil
import nltk
from nltk.corpus import stopwords
import sys
import getopt
import os
import pickle
import math
import regex
from tqdm import tqdm


from TermDictionary import TermDictionary
from Node import Node
from SPIMI import SPIMIInvert, binaryMerge

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    tempFile = 'temp.txt'
    workingDirectory = "workingDirectory/"
    limit = 10 # max number of docs to be processed at any 1 time. production = 8096, testing = 20
    result = TermDictionary(out_dict)

    # set up temp directory for SPIMI process
    if not os.path.exists(workingDirectory):
        os.mkdir(workingDirectory)
    else:
        shutil.rmtree(workingDirectory) #delete the specified directory tree for re-indexing purposes
        os.mkdir(workingDirectory)

    # sortedDocIDs = sorted([int(doc) for doc in os.listdir(in_dir)]) #sorted list of all docIDs in corpus
    fileID = 0
    stageOfMerge = 0
    count = 0
    tokenStreamBatch = []
    docLengthsAndTopTerms = {} # {docID : [length, [term1, term2], docID2 : [length, [term3, term4], ...}, to be added dumped into the postings file with its pointer stored in the final termDictionary file
    docIDSet = set()
    
    maxInt = sys.maxsize
    while True:
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt / 10)

    totalCount = 0 # testing code
    with open(input_directory, newline='', encoding='UTF-8') as f:
        reader = csv.reader(f)

        for row, col in tqdm(enumerate(reader)): # no. of iterations = no. of documents to process
            if row == 0:
                continue # skips row 0 (to avoid procesing field names)

            docID, title, content, date, court = col

            if (int(docID)) in docIDSet: # deals with duplicate docIDs
                continue

            docIDSet.add(int(docID))
            tokenStreamAndTopTerms = generateProcessedTokenStream(content)
            tokenStream = tokenStreamAndTopTerms[0]
            topTerms = tokenStreamAndTopTerms[1]
            docLengthsAndTopTerms[docID] = [len(tokenStream), topTerms]
            tokenStreamBatch.append((int(docID), tokenStream))
            count += 1
            totalCount += 1 # testing code

            if totalCount == 55: # testing code
                break

            if count == limit: # no. of docs == limit
                outputPostingsFile = workingDirectory + 'tempPostingFile' + str(fileID) + '_stage' + str(stageOfMerge) + '.txt'
                outputDictionaryFile = workingDirectory + 'tempDictionaryFile' + str(fileID) + '_stage' + str(stageOfMerge) + '.txt'
                SPIMIInvert(tokenStreamBatch, outputPostingsFile, outputDictionaryFile)
                fileID += 1
                count = 0 # reset counter
                tokenStream = [] # clear tokenStream

        
        if count > 0: # in case the number of files isnt a multiple of the limit set
            outputPostingsFile = workingDirectory + 'tempPostingFile' + str(fileID) + '_stage' + str(stageOfMerge) + '.txt'
            outputDictionaryFile = workingDirectory + 'tempDictionaryFile' + str(fileID) + '_stage' + str(stageOfMerge) + '.txt'
            SPIMIInvert(tokenStreamBatch, outputPostingsFile, outputDictionaryFile)
            fileID += 1 # passed into binary merge, and it will be for i in range(0, fileID, 2) --> will cover everything

        # inverting done. Tons of dict files and postings files to merge
        binaryMerge(workingDirectory, fileID, tempFile, out_dict)
        result = TermDictionary(out_dict)
        result.load()

        convertToPostingNodes(out_postings, tempFile, result) # add skip pointers to posting list and save them to postings.txt
        
        # add docLengthsAndTopTerms into output postings file, and store a pointer in the resultant dictionary.
        with open(out_postings, 'ab') as f: # append to postings file
            pointer = f.tell()
            result.addPointerToDocLengthsAndTopTerms(pointer)
            pickle.dump(docLengthsAndTopTerms, f)

    result.save()

    os.remove(tempFile)
    shutil.rmtree(workingDirectory, ignore_errors=True)


def generateProcessedTokenStream(content):
    stemmer = nltk.stem.PorterStemmer()
    countOfTerms = {}

    rawTokens = nltk.tokenize.word_tokenize(content) # an array of individual terms (consisting of words, standalone punctuations and numbers)
    legitTokens = [removeNonAlphanumeric(term) for term in list(filter(isNotPunctuation, rawTokens))] # no standalone punctuations, this is tokensNoStopWords in testing, and processedTokens_1 in production
    stopWordSet = set(stopwords.words('english'))
    tokensNoStopWords = [token for token in legitTokens if token.lower() not in stopWordSet] # remove all occurrences of stopwords
    stemmedTerms = []

    for word in tokensNoStopWords:
        stemmedWord = stemmer.stem(word.lower())
        stemmedTerms.append(stemmedWord)

        if stemmedWord in countOfTerms:
            countOfTerms[stemmedWord] += 1
        
        else:
            countOfTerms[stemmedWord] = 1

    weightOfTerms = {term : 1 + math.log10(value) for term, value in countOfTerms.items()} # no idf, deals with unique terms only
    top2Terms = sorted(weightOfTerms, key=weightOfTerms.get, reverse=True)[:2] # get a list containing the top 2 "heaviest" (most important) terms from the document.
    lengthOfDocVector = math.sqrt(sum([count**2 for count in weightOfTerms.values()]))

    output = [(term, weightOfTerms[term], lengthOfDocVector) for term in stemmedTerms] # all terms in a particular document, and its associated term weight, and length of vector

    return (output, top2Terms)  # returns a list of processed terms in the form of [(term1, weight, docVectorLength), (term2, weight, docVectorLength), ...], and a list of 2 most heavily weighted terms.


def isNotPunctuation(token):
    if token in string.punctuation:
        return False
    
    return True


def isNumeric(string):
    if regex.match(r'[0-9]+[^0-9][0-9]+', string):
        return True
    else:
        return False


def removeNonAlphanumeric(string):
    if not isNumeric(string):
        return regex.sub(r'[^a-zA-Z0-9\_\-\p{Sc}]', ' ', string)
    else:
        return string


def convertToPostingNodes(out_postings, file, termDictionary):
    """
    We convert all postings in the postings file into Node objects,
    where each Node object stores a docID, the term frequency in document <docID>, 
    the term weight, and the vector length of document <docID>.
    These Node objects are saved into out_postings.
    """
    with open(file, 'rb') as ref:
        with open(out_postings, 'wb') as output:

            termDict = termDictionary.getTermDict()
            for term in termDict:
                pointer = termDict[term][1] # retrieves pointer associated to the term
                ref.seek(pointer)
                docIDsDict = pickle.load(ref) # loads a dictionary of docIDs

                # postingsNodes = [Node(docID, docIDsDict[docID][0], docIDsDict[docID][1], docIDsDict[docID][2], docIDsDict[docID][3]) for docID in docIDsDict] # create Nodes
                postingsNodes = [(docID, docIDsDict[docID][0], docIDsDict[docID][1], docIDsDict[docID][2], docIDsDict[docID][3]) for docID in docIDsDict] # create 5-tuples as "Nodes" to save space
                insertSkipPointers(postingsNodes, len(postingsNodes))
                newPointer = output.tell() # new pointer location
                pickle.dump(postingsNodes, output)
                termDictionary.updatePointerToPostings(term, newPointer) # term entry is now --> term : [docFreq, pointer]


def insertSkipPointers(nodeArray, length):
    """
    Given an array of postings Nodes, add skip pointers into a Node at regular skip intervals
    and output an array of Nodes with skip pointers.
    """
    skipInterval = int(math.sqrt(length))
    endOfIndex = length - 1
    currentIndex = 0
    insertionIndex = 2

    for node in nodeArray:
        skipPointer = (0,)
        if (currentIndex % skipInterval == 0 and currentIndex + skipInterval <= endOfIndex):
            # makes sure that it is time for a skip pointer to be inserted and it is not inserted into
            # a node that will facilitate a skip past the last node.
            
            # node.addSkipPointer(skipInterval)
            skipPointer = (skipInterval,)

        nodeArray[currentIndex] = node[ :insertionIndex] + skipPointer + node[insertionIndex: ]

        currentIndex += 1


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
