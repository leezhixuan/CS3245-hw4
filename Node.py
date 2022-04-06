class Node(object):
    """
    Node is a class that stores a docID, its skip pointer, the term frequency in document <docID>, the term weight, and the vector length of document <docID>.
    """

    def __init__(self, docID, termFrequency, termWeight, vectorDocLength, positionalList):
        self.docID = docID
        self.termFrequency = termFrequency
        self.termWeight = termWeight
        self.vectorDocLength = vectorDocLength
        self.positionalList = positionalList
        self.skipPointer = 0  # target index = skipPointer + currentIndex


    def getTermFrequency(self):
        return self.termFrequency


    def getTermWeight(self):
        return self.termWeight


    def getVectorDocLength(self):
        return self.vectorDocLength


    def getPositionalList(self):
        return self.positionalList


    def __str__(self):
        return str(self.docID)


    def __repr__(self):
        return "(" + str(self.docID) + ", " + str(self.termFrequency) + ", " + str(self.skipPointer) + ", " + str(self.termWeight) + ", " + str(self.vectorDocLength) + ", " + str(self.positionalList) + ")"


    def getDocID(self):
        return self.docID


    def addSkipPointer(self, value):
        """
        Adds a skip pointer to the Node
        """
        self.skipPointer = value


    def hasSkip(self):
        """
        Checks if the Node contains a skip pointer.
        """
        return self.skipPointer != 0
