import pickle

class TermDictionary(object):
    """
    TermDictionary is a class that encapsulates the attributes and behaviour of a dictionary in indexes.
    """

    DOCFREQ_INDEX = 0
    POINTERS_INDEX = 1

    def __init__(self, storageLocation):
        # In the form of {term: [docFrequency, pointer], term2: [docFrequency, pointer], ..., termN: [docFrequency, pointer]}
        # In the form of {term: [docFrequency, pointer], term2: [docFrequency, pointer], ..., "d0cum3ntL3ngth": pointer} (after indexing)
        self.termInformation = {} 
        self.storageLocation = storageLocation


    def addTerm(self, term, docFrequency, pointer):
        """
        Given a term, its document frequency and a pointer to where its (partial) postings list is stored,
        adds these information into the dictionary.
        """
        if term in self.termInformation.keys(): # if given term already exists
            self.termInformation[term][self.DOCFREQ_INDEX] += docFrequency
        
        else: # term does not exist
            self.termInformation[term] = [docFrequency, pointer] # creates a new key-value pair in the dictionary.
    

    def getTermPointer(self, term):
        try: 
            # if given term exists in the dictionary
            termPointers = self.termInformation[term][self.POINTERS_INDEX]
            return termPointers
            
        except KeyError: # given term does not exist in the dictionary
            return -1


    def getAllKeys(self):
        return self.termInformation.keys()
    

    def save(self):
        """
        Saves term information held in the storage location specified
        """
        with open(self.storageLocation, 'wb') as f:
            pickle.dump(self.termInformation, f)


    def load(self):
        """
        Loads term information held at the specified storage location
        """
        with open(self.storageLocation, 'rb') as f:
            self.termInformation = pickle.load(f)


    def updatePointerToPostings(self, term, newPointer):
        """
        Given term, updates its existing pointer list with the new pointer list provided.
        """
        self.termInformation[term][self.POINTERS_INDEX] = newPointer


    def getTermDict(self):
        return self.termInformation


    def getTermDocFrequency(self, term):
        try: 
            # if term exists in the dictionary
            docFrequency = self.termInformation[term][self.DOCFREQ_INDEX]
            return docFrequency

        except KeyError: # term does not exist in the dictionary
            return 0
            
    
    def addPointerToDocLengths(self, pointer):
        """
        Adds a pointer to a dictionary where key = docID, value = length of document with ID = docID.
        """
        self.termInformation["d0cum3ntL3ngth"] = pointer

    
    def getPointerToDocLengths(self):
        return self.termInformation["d0cum3ntL3ngth"]
    