import nltk
from nltk.corpus import wordnet

def expandQuery(query):
    """
    Given a query string, we return an expanded query string containing 3 synonyms of each term in the original query string.
    """
    stemmer = nltk.stem.porter.PorterStemmer()

    queryTerms = nltk.tokenize.word_tokenize(query)
    synsetsFromQueryTerms = getSynsets(queryTerms)

    result = []

    index = 0
    for synsetsList in synsetsFromQueryTerms:
        synonymList = getTop3Synonyms(synsetsList)
        words = [synonym.lemma_names()[0] for synonym in synonymList]
        queryTerm = queryTerms[index]

        if queryTerm not in words:
            words.insert(0, queryTerm)

        stemmed = [stemmer.stem(word.lower()) for word in words]
        result.extend(stemmed)

        index += 1

    return ' '.join(result)
        

def getSynsets(queryTerms):
    """
    Given a list of query terms, returns a list of (distinct) synsets associated to each query term.
    """
    taggedTerms = nltk.pos_tag(queryTerms) # in the form of [(‘Hello’, ‘NNP’), (‘Guru99’, ‘NNP’), (‘,’, ‘,’), (‘You’, ‘PRP’), (‘have’, ‘VBP’)]

    result = []

    for term in taggedTerms:
        word = term[0]
        tag = term[1]
        wordNetTag = convertToWordNetTag(tag)

        if wordNetTag == '':
            continue

        synsets = wordnet.synsets(word, pos=wordNetTag) # in the form of [Synset('dog.n.01'), Synset('frump.n.01'), Synset('dog.n.03'), Synset('cad.n.01'), ...]
        uniqueSynsets = removeDuplicates(synsets)
        result.append(uniqueSynsets)

    return result # in the form of [[synsets for queryTerm], [synsets for queryTerm1], [synsets for queryTerm2], ...]

    
def convertToWordNetTag(posTag):
    """
    Replaces the given posTag with their WordNet equivalent taggings.
    """
    if posTag.startswith('J'):
        return wordnet.ADJ

    elif posTag.startswith('V'):
        return wordnet.VERB

    elif posTag.startswith('N'):
        return wordnet.NOUN

    elif posTag.startswith('R'):
        return wordnet.ADV

    else:
        return ''


def removeDuplicates(synsets):
    """
    Given a set of synonyms, duplicates amongst them are discarded.
    Two synonyms are deemed to be duplicates solely based on spelling.
    The result is a a set of unique synonyms.
    """
    result = []
    wordSet = set()

    for synset in synsets:
        word = synset.lemma_names()[0] # gets the word from the synset

        if word in wordSet:
            # skips to the next iteraion without adding 
            continue

        wordSet.add(word)
        result.append(synset)

    return result


def getTop3Synonyms(synsets):
    """
    Given synsets, we return the top 3 closest synonyms (which may include the word itself).
    """
    datumSynonym = synsets[0] # synsets are ordered by frequency, thus index 0 = most frequent, they're most frequently used for some reason

    synonymScorePairs = []
    for i in range(len(synsets)):
        similarityScore = datumSynonym.path_similarity(synsets[i])
        synonymScorePair = (synsets[i], similarityScore)
        synonymScorePairs.append(synonymScorePair)

    synonymScorePairs.sort(key=lambda tup: tup[1]) # sort based on similarity score, in place.

    return synonymScorePairs[:3]
