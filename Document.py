class Document(object):
    """
    Document is a class that stores a docID, and the weight of docuemnt <docID>.
    The purpose of the this class to to faciliate ranking of documents when the heapq library is used.
    """

    def __init__(self, docID, weight):
        self.docID = docID
        self.weight = weight

    
    def getWeight(self):
        return self.weight


    def __repr__(self):
        return "[" + str(self.docID) + ", " + str(self.weight) + "]"


    def __str__(self):
        return str(self.docID)


    def __eq__(self, otherDoc):
        """
        Defines how 2 Documents are deemed equal (magnitude-wise).
        """
        if isinstance(otherDoc, Document):
            return self.weight == otherDoc.weight

        return False


    def __ne__(self, otherDoc):
        """
        Defines how 2 Documents are deemed unequal (magnitude-wise).
        """
        if isinstance(otherDoc, Document):
            return self.weight != otherDoc.weight

        return False


    def __le__(self, otherDoc):
        """
        Defines how the this Document is less than or equal to the other Document (magnitude-wise).
        """
        if isinstance(otherDoc, Document):
            return self.weight <= otherDoc.weight

        return False


    def __ge__(self, otherDoc):
        """
        Defines how the this Document is greater than or equal to the other Document (magnitude-wise).
        """
        if isinstance(otherDoc, Document):
            return self.weight >= otherDoc.weight

        return False 


    def __lt__(self, otherDoc):
        """
        Defines how the this Document is strictly less than the other Document (magnitude-wise).
        """
        if isinstance(otherDoc, Document):
            return self.weight < otherDoc.weight

        return False


    def __gt__(self, otherDoc):
        """
        Defines how the this Document is strictly greater than the other Document (magnitude-wise).
        """
        if isinstance(otherDoc, Document):
            return self.weight > otherDoc.weight

        return False