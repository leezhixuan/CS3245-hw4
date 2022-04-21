This is the README file for A0223846B, A0199384J, A0174119E and A0194090E's submission
Email(s): e0564887@u.nus.edu; e0406365@u.nus.edu; e0205114@u.nus.edu; e0373913@u.nus.edu


== Python Version ==

We're using Python Version 3.8.3 for this assignment.


== General Notes about this assignment ==
- Indexing -

We modified the SPIMI method of indexing terms in the corpus. A temporary working directory is 
specially set up to store intermediate files during the SPIMI process. The maximum number of documents that we 
process before making the calling SPIMIInvert() is 8096. For every document in the corpus, we make a call 
to generateProcessedTokensStream(). In this method, we keep a counter for every term encountered as well 
as stem and apply case-folding to every term. Stopwords are also removed in this method. We also calculate their 
weights using 1 + log10(termFrequency), without idf. By determining the weights of each term in the document, we 
can calculate the vector length of the document. With the weights of each term calculated, we can determine the top 2
most important words in a particular document based on term weights. We store these 2 terms in a list. In the end, we 
will be able to output a tuple of 2 elements: the first being a list of tuples of (term, docID, weight,lengthOfDocVector) 
and the second being a list of 2 most important words from a particular document.

After processing each document via generateProcessedTokensStream(), the resultant list of tuples is added to tokenStreamBatch. 
The list of 2 most important terms associated to that particular document, along with the length of that document is added to 
docLengthsAndTopTerms, where each entry is in the form of docID : [docLength, [importantTerm1, importantTerm2]].

During SPIMIInvert(), terms and their docID, termFrequency, termWeight and docVectorLength are being consolidated into temporary
dictionary and postings file. It is also here that positional indexes asoociated to each term (from a particular document) are created.

After all the documents in the corpus have been processed. We make a call to binaryMerge() and it is in charge of 
merging all the existing "dictionary" and "postings" files that have been created into a single "dictionary" and 
"postings" file. 

At this stage, postings are in the form of a 5-tuple. They are in the form of (docID, termFrequency, termWeight, 
docVectorLength, positionalIndexes). We convert these 5-tuples into 6-tuples by inserting skip pointers next. By the end,
the 6-tuples created are in the form of (docID, termFrequency, skipPointer, termWeight, docVectorLength, positionalIndexes).

Finally, we load the TermDictionary up so that we can add a pointer that points to the dictionary which stores the 
length of all documents in the corpus. We then save the information in TermDictionary onto the disk. At this point, 
we delete the temporary file that was used to store postings, as well as the temporary directory used by the SPIMI process.

The final format of each postings list is a list of 6-tuple, where each tuple is:
(docID, termFrequency, skipPointer, termWeight, docVectorLength, positionalIndexes)

The dictionary in the TermDictionary object will be in the form of:
{term: [docFrequency, pointer], term2: [docFrequency, pointer], ..., ""d0cum3ntL3ngth4ndT0pT3rm5"": pointer}

- Searching -
Before the query is processed, we make sure that the query is valid by checking that it is not a mix of free text and boolean or free text and phrasal.
The query is also checked to contain the correct number of quotations and AND operators.

_Boolean Search_

We preprocess terms in Boolean queries the same way we process words in the corpus. For each
Boolean query, we rely on the Shunting-yard algorithm to turn the query into its post-fix form
(Reverse Polish Notation). We then evaluate this post-fix form with the help of the Operand
class as well as the Stack data structure, and append each query result onto a new line in the results file.
In the case of invalid queries, we output an empty string onto a new line in the results file.

The general idea of the AND function is as such: The postings of both search terms are
retrieved. With pointers at both starts of the postings, we add the posting to the result if both
posting lists contain said posting. We then advance the list with the smaller docID (both lists
should already be sorted by docID). Another check will be conducted to determine if the taking the skip pointer 
is feasible (i.e. will skip to a posting that is smaller than that of the other posting list), should there be one 
available. Once both lists are fully iterated, the result is output.

There are 3 auxillary functions for Boolean Search: (purely conjunctive for this homework)
1) evalAND_terms - where both operands are query terms, and posting lists belonging to both will
be retrieved and compared so that we are able to find the common ones between the 2.

2) evalAND_term_result - where one Operand is a search term, and the other being a list of docIDs.
The posting list for the term will be retrieved before it is compared with the other to find the ones
that they share.

3) evalAND_results - where both search terms exists in result form i.e. both are posting lists.
Here, we can simply find the intersection between the 2 postings lists.

Auxillary functions make use of set() to ensure no duplicates and traverse skip pointers accordingly.

Output is an Operand object that contains a result only. The result is a postings list containing all docIDs
common to the 2 input Operands, sorted in ascending order.

_Phrasal Search_

For one-worded phrases, we simply retrieved the postings list associated with that phrase.

For phrases with more than one word, we retrieve the posting lists of each word and find a set of common docIDs. 
For each matched docID, we check the positional index of each word to make sure they appear consecutively in the document.
If the query returns too little docIds, the result will be appended with free text query (by breaking up phrases into 
individual terms to form free texts) result.

_Free Text Search_

We preprocess terms in queries the same way we preprocess words in the corpus (only stemming and case-folding) so that we
will be able to search effectively. In CosineScores(), we also calculate score of each document based on lnc.ltc 
(in terms of SMART notation of ddd.qqq). As such, weights of query terms are determined using (1 + log10(tf)) * idf, with cosine normalisation.
For each query term, we add (normalisedQueryTermWeight * DocumentTermWeight) / docVectorLength to the score of every document in its postings list. 
At the end, every document would have obtained a score. The higher the score, the more relevant that particular document is to the query.

In order to rank and output the top relevant documents to the query, we utilise the heapq library as well as the Document class.
The Document class helps to facilitate ranking. As such, we convert every document-score pair into Document objects and pass the array
of Document objects into heapq.extract10(). Then, we filter away any document with a score = 0 that somehow managed to make it into the top 10.
Thereafter, we write the top results into the output file, each on a new line.


= Bonus (Query Refinement) =

Details of experimential results and analysis regarding the query refinement techniques that we have implemented can be found in BONUS.docx.
Below is a gist of the ideas for our query refinement methods.

- Query Expansion -

Given a query string, we tokenize them into individual query terms. Then, we perform part-of-speech tagging on each one of them and convert
those tags into their WordNet equivalent ones. At the end, we retrieve their synsets using wordnet.synsets().

We remove duplicates from the retrieved synsets. 2 synonyms are deemed to be duplicates if they are spelt the same way, regardless of semantics.

Another concern is that there may be query terms that have plenty of synonyms. As such, we look to restrict the number of synonyms we add to 
the original query string so that querying does not become a time-intensive process.

Here, we take only the top 3 synoyms from each query term. To rank synonyms, we turn to synset1.pathsimilarity(synset2) to generate a score.
pathsimilarity() returns a score denoting how similar 2 word senses are based on the shortest path that connects the senses in the this is-a 
(hypernym/hypnoym) taxonomy. The score is in the range of 0 to 1. A score of 1 represents identity.

The top 3 synonyms belonging to each query term is then added to the query string for another round of querying.

- Pseudo relevance feedback -

After a round of querying using the original query string that was given by the user, we obtain a list of docID as results. We take treat the 
top k highest ranking docIDs to be relevant documents.

Using the Rocchio formula approach for relevance feedback requires our indexing to store space-intensive document-vectors (rather than term-vectors, 
which are currently used) so that their centroid can be calculated.As it is computationally expensive to calculate the centroid of these relevant, 
we make use of the important terms associated to each docID that we have stored during indexing. For each of the top k most relevant docIDs, we retrieve 
their important terms and add them into the query string to form a new query string. We then do another round of querying with this new query string.

This is somewhat similar to query expansion. The main difference is that the "expansion" here comes from the first round of query results rather
than from the synonyms (from WordNet) added. The words added may or may not be synonyms of the query terms in the original query string.


== Work Allocation ==

A0223846B - Indexing, Phrasal Search, Query Expansion, Pseudo Relevance Feedback, README.txt and BONUS.docx
A0194090E - Phrasal Search, Free Text Search, Query Expansion, README.txt
A0174119E - Pseudo Relevance Feedback, BONUS.docx
A0199384J - Boolean Search, Pseudo Relevance Feedback


== Files included with this submission ==

README.txt - (this), general information about the submission.

index.py - main running code, indexes documents in the corpus into a postings file via SPIMI, and creates
a dictionary file.

Document.py - a helper class that facilitates the ranking of documents (based on their score) at the end of free text search.

free_text.py - contains functions to facilitate free text queries using cosine scores and tf-idf

phrasal.py - contains functions to allow for phrasal queries through matching positional indexes within a document.

pseudoRF.py - contains functions to enable pseudo relevance feedback.

postings_util - contains helper functions to operate with 6-tuples (postings)

query_expansion.py - contains functions to make query expansions possible via the addition of (closest) synonyms to the current query string.

Operand.py - a helper class to represent intermediate results during Boolean queries.

search.py - main running code, searches for postings of terms based on queries and outputs the top ten (or less)
results, ranked by lnc.ltc, to a file.

SPIMI.py - implements SPIMI scalable index construction.

TermDictionary.py - the TermDictionary class, the main object type used to store term information: term,
its document frequency, and the pointer to fetch its postings in the postings file.

dictionary.txt - saved output of dictionary information of TermDictionary: contains terms, their document
frequency as well as their pointer. It also contains a special key, "d0cum3ntL3ngth", whose value is a pointer to 
a dictionary whose key-value pair is docID : docLength.

postings.txt - saved output of list of Nodes objects, as well as a dictionary whose key-pair value is docID : docLength.

BONUS.docx - details the experimential results and analysis of the query refinement techniques that we have implemented for HW4


== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0223846B, A0199384J, A0174119E and A0194090E certify that we have followed the CS 3245 Information Retrieval class
guidelines for homework assignments.  In particular, we expressly vow that we have followed the Facebook
rule in discussing with others in doing the assignment and did not take notes (digital or printed) from
the discussions.

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>


== References ==

Introduction To Information Retrieval - Cambridge University Press (textbook)
https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072
https://www.kaggle.com/code/nikhilkhetan/tqdm-tutorial/notebook
https://www.guru99.com/pos-tagging-chunking-nltk.html#:~:text=POS%20Tagging%20in%20NLTK%20is,each%20word%20of%20the%20sentence.
https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
https://github.com/tqdm/tqdm
https://www.nltk.org/howto/wordnet.html
https://wordnet.princeton.edu/documentation/wn1wn
