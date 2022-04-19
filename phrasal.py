import nltk
import pickle
from postings_util import getDocID, getPositionalIndexes

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

def processPharsalQuery(query, termDict, postingsFile):
    """
    Takes in the query (phrasal), the TermDictionary object and the name of the postings file (.txt).
    Returns a list of docIDs.
    """
    queryTerms = nltk.word_tokenize(query)

    if len(queryTerms) == 1:
        pointer = termDict.getTermPointer(queryTerms[0])
        postings = retrievePostingsList(postingsFile, pointer)

        return [getDocID(node) for node in postings]

    elif len(queryTerms) == 2:
        pointer1 = termDict.getTermPointer(queryTerms[0])
        pointer2 = termDict.getTermPointer(queryTerms[1])
        postings1 = retrievePostingsList(postingsFile, pointer1)
        postings2 = retrievePostingsList(postingsFile, pointer2)

        result = twoTermPhrasalHelper(postings1, postings2)
        return result

    elif len(queryTerms) == 3:
        pointer1 = termDict.getTermPointer(queryTerms[0])
        pointer2 = termDict.getTermPointer(queryTerms[1])
        pointer3 = termDict.getTermPointer(queryTerms[2])
        postings1 = retrievePostingsList(postingsFile, pointer1)
        postings2 = retrievePostingsList(postingsFile, pointer2)
        postings3 = retrievePostingsList(postingsFile, pointer3)

        result = threeTermPhrasalHelper(postings1, postings2, postings3)
        return result
    else:
        return []


def twoTermPhrasalHelper(postings1, postings2):
    """
    Given 2 postings lists, return a list of docIDs containing the given phrase.
    """
    marker1 = 0
    marker2 = 0

    result = []

    while (marker1 < len(postings1)) and (marker2 < len(postings2)):
        docID_1 = getDocID(postings1[marker1])
        docID_2 = getDocID(postings2[marker2])

        if docID_1 == docID_2:
            positionalList1 = getPositionalIndexes(postings1[marker1])
            positionalList2 = getPositionalIndexes(postings2[marker2])

            if isPhraseInTwoPositionalList(positionalList1, positionalList2):
                result.append(docID_1)

            marker1 += 1
            marker2 += 2

        elif docID_1 < docID_2:
            marker1 += 1

        else:
            marker2 += 1

    return result


def threeTermPhrasalHelper(postings1, postings2, postings3):
    """
    Given 3 postings lists, returns a list of docIDs that contains the 3 word phrase.
    """
    marker1 = 0
    marker2 = 0
    marker3 = 0

    result = []

    while (marker1 < len(postings1)) and (marker2 < len(postings2)) and (marker3) < len(postings3):
        docID_1 = getDocID(postings1[marker1])
        docID_2 = getDocID(postings2[marker2])
        docID_3 = getDocID(postings3[marker3])

        if docID_1 == docID_2 and docID_2 == docID_3:
            positionalList1 = getPositionalIndexes(postings1[marker1])
            positionalList2 = getPositionalIndexes(postings2[marker2])
            positionalList3 = getPositionalIndexes(postings3[marker3])

            if (isPhraseInThreePositionalList(positionalList1, positionalList2, positionalList3)):
                result.append(docID_1)

            marker1 += 1
            marker2 += 1
            marker3 += 1
        
        # increment the value of the smallest marker amongst the 3.
        elif docID_1 <= docID_2 and docID_1 <= docID_3:
            marker1 += 1

        elif docID_2 <= docID_1 and docID_2 <= docID_3:
            marker2 += 1

        else: # marker3 is the smallest
            marker3 += 1

    return result
            


def isPhraseInTwoPositionalList(positionalList1, positionalList2):
    """
    Given 2 positional lists (positionalList1 belongs to queryTerm_1, positionalList2 belongs to queryTerm_2),
    returns True if the documents contains the 2 word phrase and False otherwise.
    """
    marker1 = 0
    marker2 = 0
    position_1 = 0 # with postings compression
    position_2 = 0 # with postings compression

    while (marker1 < len(positionalList1)) and (marker2 < len(positionalList2)):
        # with postings compression
        position_1 += positionalList1[marker1]
        position_2 += positionalList2[marker2]

        # without postings compression
        # position_1 = positionalList1[marker1]
        # position_2 = positionalList2[marker2]

        if position_1 + 1 == position_2:
            return True
        
        elif position_1 >= position_2:
            marker2 += 1

        else:
            marker1 += 1

    return False


def isPhraseInThreePositionalList(positionalList1, positionalList2, positionalList3):
    """
    Given 3 postings lists (postingsList1 belongs to the 1st term, postingsList2 belongs to the 2nd term, 
    and postingsList3 belongs to the 3rd term.), return True if they contain the 3 word phrase and False 
    otherwise.
    """

    marker1 = 0
    marker2 = 0
    marker3 = 0
    position_1 = 0 # with postings compression
    position_2 = 0 # with postings compression
    position_3 = 0 # with postings compression

    while (marker1 < len(positionalList1)) and (marker2 < len(positionalList2)) and (marker3 < len(positionalList3)):
        # with postings compression
        position_1 += positionalList1[marker1]
        position_2 += positionalList2[marker2]
        position_3 += positionalList3[marker3]

        # without postings compression
        # position_1 = positionalList1[marker1]
        # position_2 = positionalList2[marker2]
        # position_3 = positionalList3[marker3]

        if (position_1 + 1 == position_2) and (position_2 + 1 == position_3):
            return True

        elif position_1 >= position_2:
            marker2 += 1

        elif position_1 >= position_3 or position_2 >= position_3:
            marker3 += 1

        else:
            marker1 += 1 # eventually, marker 2 and marker 3 will increment itself accordingly.

    return False

