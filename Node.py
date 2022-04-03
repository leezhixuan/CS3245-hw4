class Node(object):
    """
    Node is a class that stores a docID, the term frequency in document <docID>, the term weight, and the vector length of document <docID>.
    """

    def __init__(self, docID, termFrequency, termWeight, vectorDocLength):
        self.docID = docID
        self.termFrequency = termFrequency
        self.termWeight = termWeight
        self.vectorDocLength = vectorDocLength


    def getTermFrequency(self):
        return self.termFrequency


    def getTermWeight(self):
        return self.termWeight


    def getVectorDocLength(self):
        return self.vectorDocLength


    def __str__(self):
        return str(self.docID)


    def __repr__(self):
        return "(" + str(self.docID) + ", " + str(self.termFrequency) + ", " + str(self.termWeight) + ", " + str(self.vectorDocLength) +")"


    def getDocID(self):
        return self.docID