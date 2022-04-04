#!/usr/bin/python3
import csv
import regex
import string
import shutil
import nltk
from nltk.corpus import stopwords
import sys
import getopt
import os
import pickle
import math
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
    limit = 1024 # max number of docs to be processed at any 1 time.
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
    docLengths = {} # {docID : length, docID2 : length, ...}, to be added dumped into the postings file with its pointer stored in the final termDictionary file
    
    maxInt = sys.maxsize
    while True:
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt / 10)

    with open(input_directory, newline='', encoding='UTF-8') as f:
        reader = csv.reader(f)

        for row, col in tqdm(enumerate(reader)):
            if row == 0:
                continue # skips row 0 (to avoid procesing field names)

            docID, title, content, date, court = col
            tokenStream = generateProcessedTokenStream(content, docID)
            docLengths[docID] = len(tokenStream)
            tokenStreamBatch.append(tokenStream)
            count+=1

            if count == limit: # no. of docs == limit
                outputPostingsFile = workingDirectory + 'tempPostingFile' + str(fileID) + '_stage' + str(stageOfMerge) + '.txt'
                outputDictionaryFile = workingDirectory + 'tempDictionaryFile' + str(fileID) + '_stage' + str(stageOfMerge) + '.txt'
                SPIMIInvert(tokenStream, outputPostingsFile, outputDictionaryFile)
                fileID+=1
                count = 0 # reset counter
                tokenStream = [] # clear tokenStream

        
        if count > 0: # in case the number of files isnt a multiple of the limit set
            outputPostingsFile = workingDirectory + 'tempPostingFile' + str(fileID) + '_stage' + str(stageOfMerge) + '.txt'
            outputDictionaryFile = workingDirectory + 'tempDictionaryFile' + str(fileID) + '_stage' + str(stageOfMerge) + '.txt'
            SPIMIInvert(tokenStream, outputPostingsFile, outputDictionaryFile)
            fileID+=1 # passed into binary merge, and it will be for i in range(0, fileID, 2) --> will cover everything

        #inverting done. Tons of dict files and postings files to merge
        binaryMerge(workingDirectory, fileID, tempFile, out_dict)
        result = TermDictionary(out_dict)
        result.load()

        convertToPostingNodes(out_postings, tempFile, result) # add skip pointers to posting list and save them to postings.txt
        
        # add docLengths into output postings file, and store a pointer in the resultant dictionary.
        with open(out_postings, 'ab') as f: # append to postings file
            pointer = f.tell()
            result.addPointerToDocLengths(pointer)
            pickle.dump(docLengths, f)

    result.save()

    os.remove(tempFile)
    shutil.rmtree(workingDirectory, ignore_errors=True)


def generateProcessedTokenStream(content, docID):
    stemmer = nltk.stem.PorterStemmer()
    countOfTerms = {}

    rawTokens = nltk.tokenize.word_tokenize(content) # an array of individual terms (consisting of words, standalone punctuations and numbers)
    processedTokens_1 = list(filter(isNotPunctuation, rawTokens)) # no standalone punctuations
    # print(tokenNoPunctuations)
    tokensNoStopWords = [token for token in processedTokens_1 if token.lower() not in stopwords.words('english')] # remove all occurrences of stopwords
    # print(tokensNoStopWords)

    for word in tokensNoStopWords:
        stemmedWord = stemmer.stem(word.lower())

        if stemmedWord in countOfTerms:
            countOfTerms[stemmedWord] += 1
        
        else:
            countOfTerms[stemmedWord] = 1

    weightOfTerms = {term : 1 + math.log10(value) for term, value in countOfTerms.items()} # no idf
    lengthOfDocVector = math.sqrt(sum([count**2 for count in weightOfTerms.values()]))

    output = [(term, docID, weight,lengthOfDocVector) for term, weight in weightOfTerms.items()] # all terms in a particular document, and its associated term weight, and length of vector

    return output  # returns a list of processed terms in the form of [(term1, docID, weight, docVectorLength), (term2, docID, docVectorLength), ...]


def isNotPunctuation(token):
    if token in string.punctuation:
        return False
    
    return True


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

                postingsNodes = [Node(docID, docIDsDict[docID][0], docIDsDict[docID][1], docIDsDict[docID][2]) for docID in docIDsDict] # create Nodes
                newPointer = output.tell() # new pointer location
                pickle.dump(postingsNodes, output)
                termDictionary.updatePointerToPostings(term, newPointer) # term entry is now --> term : [docFreq, pointer]


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
