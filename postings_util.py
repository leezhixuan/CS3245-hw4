"""
This file contains functions to help with readability during retrieval
Postings are stored as 6-tuples in the form of (docID, termFrequency, skipPointer, termWeight, docVectorLength, positionalIndexes)
"""

def getDocID(postingTuple : tuple):
    return postingTuple[0]


def getTermFrequency(postingTuple : tuple):
    return postingTuple[1]


def hasSkipPointer(postingTuple : tuple):
    return postingTuple[2] != 0


def getSkipPointer(postingTuple : tuple):
    return postingTuple[2]


def getTermWeight(postingTuple : tuple):
    return postingTuple[3]


def getDocVectorLength(postingTuple : tuple):
    return postingTuple[4]


def getPositionalIndexes(postingTuple : tuple):
    return postingTuple[5]

