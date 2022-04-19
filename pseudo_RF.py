from TermDictionary import TermDictionary
from SPIMI import retrievePostingsDict

def PRF(docIDs : list, termDict : TermDictionary, postingsFile : str):
    """
    Given a list of docIDs and a TermDictionary object (with .load() already called), 
    return a list of important terms that are associated to those docIDs.
    """

    pointer = termDict.getPointerToDocLengthsAndTopTerms()
    docLengthsAndTopTerms = retrievePostingsDict(postingsFile, pointer)
    
    result = []

    for docID in docIDs:
        topTerms = docLengthsAndTopTerms[docID][1] # this is a list of 2 terms
        result.extend(topTerms)

    return result
        