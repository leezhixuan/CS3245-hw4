
with open('output.txt', 'r') as f:
    result = f.read()
    resultList = result.split(" ")
    print("with PRF:")
    print("\n" + "Ranking of 2211154: " + str(resultList.index("2211154") + 1))
    print("\n" + "Ranking of 2748529: " + str(resultList.index("2748529") + 1))
    # print("\n" + "Ranking of 2702938: " + str(resultList.index("2702938") + 1))
    