import pickle

# filename = 'queries/q1.txt'
# with open(filename, 'r') as f:
#     for query in f:
#         print(query)

with open('dictionary.txt', 'rb') as f:
    data = pickle.load(f)
    print(data)

# with open('postings-file.txt', 'rb') as f:
#     # f.seek(2255419) # "still"
#     # f.seek(3174674) # 'tribunal court': [55, 3174674]
#     # f.seek(1517063) # 'get': [23, 1517063]
#     # f.seek(1360148943) # 'worst': [1388, 1360148943]
#     # f.seek(1569451) # 'get': [23, 1569451],
#     # f.seek(269904) #  'respond': [4, 269904]
#     # f.seek(253990) #  'respond': [4, 253990]
#     # f.seek(274499) # 'respond': [4, 274499]
#     # f.seek(3221059) # 'respond': [30, 3221059]
#     # f.seek(2758131) # 'respond': [29, 2758131]
#     # f.seek(3221059) #'respond': [30, 3221059] # duplicate entries
#     # f.seek(2446187) #'respond': [30, 2446187] # no duplicate entries in positional list
#     # f.seek(2401381) #[30, 2401381] # gap encoding
#     f.seek(1298029) # 'respond': [30, 1298029] # tuple instead of nodes
#     pL = pickle.load(f)
#     print(pL)