import pickle

# filename = 'queries/q1.txt'
# with open(filename, 'r') as f:
#     for query in f:
#         print(query)

# with open('dictionary.txt', 'rb') as f:
#     data = pickle.load(f)
#     print(data)

with open('postings-file.txt', 'rb') as f:
    f.seek(2255419) # "still"
    pL = pickle.load(f)
    print(pL)