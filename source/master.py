import csv

from word import Word
from pprint import pprint
# import csv
# import networkx as nx
# import matplotlib.pyplot as plt
from collections import defaultdict
import itertools
from operator import itemgetter
import time
from wiktionaryparser import WiktionaryParser

allSpheresCount = defaultdict(int)  # all the words and how many times we came across them
allUniqueSpheres = []  # all the unique words that we came across including linked, and yet to be linked
allLinks = []  # all the source - target - weight links that have been created
allPairs = []
spheresAlreadyLinked = set()  # just the words that have been explored (set as source) in links


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def writeSpheresCountToCSV(filename):
    writer = csv.writer(open(filename+".csv", "wb"))
    i=0
    for wordCount in allSpheresCount:
        print '{:>20} {:>20}'.format(wordCount, allSpheresCount[wordCount])
        writer.writerow([i,wordCount, allSpheresCount[wordCount]])
        i+=1


def findGoodPairs():
    pprint(allPairs)
    for entry in allPairs:
        entry['strength'] = sum(entry['strength'])

    newlist = sorted(allPairs, key=itemgetter('strength'))

    pprint(newlist)


def searchAllPairs(first, second):
    for existingEntry in allPairs:
        if existingEntry['first'] == first and existingEntry['second'] == second:
            return allPairs.index(existingEntry);
    return -1;


def addToAllPairs(list):
    for newEntry in list:
        indexIfFound = searchAllPairs(newEntry['first'], newEntry['second'])
        if indexIfFound == -1:
            allPairs.append(newEntry)
        else:
            allPairs[indexIfFound]['strength'].extend(newEntry['strength'])


def detectPairs(newWordLinks, tempExtract):
    wordPairDistancesMaster = []

    edgesByWeight = defaultdict(list)
    for x in newWordLinks:
        edgesByWeight[x['weight']].append(x['target'])

    # pprint(edgesByWeight)
    splitSentencesOfArticle = tempExtract.lower().replace("\n", " ").split(".")

    for weightGroup in edgesByWeight.keys():

        groupedByWeight = list(itertools.combinations(edgesByWeight[weightGroup], 2))
        for pair in groupedByWeight:

            wordPairDistances = []
            for sentence in splitSentencesOfArticle:
                if pair[0] in sentence.split() and pair[1] in sentence.split():

                    order1 = (sentence.split().index(pair[0]) - sentence.split().index(pair[1]))
                    order2 = (sentence.split().index(pair[1]) - sentence.split().index(pair[0]))

                    if order1 > order2:
                        element = [element for element in wordPairDistances if element['first'] == pair[1]]
                        if len(element) > 0:
                            element[0]['strength'].append((1.0 / order1))
                        else:
                            wordPairDistances.append(
                                {'first': pair[1], 'second': pair[0], 'strength': [(1.0 / order1)]})
                    else:
                        element = [element for element in wordPairDistances if element['first'] == pair[0]]
                        if len(element) > 0:
                            element[0]['strength'].append((1.0 / order1))
                        else:
                            wordPairDistances.append(
                                {'first': pair[0], 'second': pair[1], 'strength': [(1.0 / order2)]})

            wordPairDistancesMaster.extend(wordPairDistances)
    addToAllPairs(wordPairDistancesMaster)
    # pprint(wordPairDistancesMaster)


def grabPartOfSpeech(word):
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

    parser = WiktionaryParser()
    word = parser.fetch(word)
    result = []
    if len(word) > 0:
        for entry in word[0]['definitions']:
            result.append(entry['partOfSpeech'])
    return result


def addToAllUniqueSpheres(list):
    for x in list:
        if x not in allUniqueSpheres:
            print x
            allSpheresCount[x] = 1
            allUniqueSpheres.append(x)
        else:
            allSpheresCount[x] += 1


def searchTree(i):
    if i == 1:
        return
    query = allUniqueSpheres[i]
    newWord = Word(query)
    addToAllUniqueSpheres(newWord.spheres)
    print i
    try:
        if newWord.links[0]['source'] not in spheresAlreadyLinked:
            allLinks.extend(newWord.links)
            spheresAlreadyLinked.add(query)
            detectPairs(newWord.links, newWord.extract)
            #print newWord.extract
        newWord.deleteAll()
        searchTree(i + 1)

        # streamLinks()

    except IndexError:
        # print "bad index"
        newWord.deleteAll()
        searchTree(i + 1)


t1 = time.time()

allUniqueSpheres.append("los angeles")

searchTree(0)



#findGoodPairs()



# pprint(allLinks)
# pprint(allUniqueSpheres)


t2 = time.time()
print "time: ", t2 - t1
print len(allUniqueSpheres)




# # Basic import
# from gephistreamer import graph
# from gephistreamer import streamer
#
# # Create a Streamer
# # adapt if needed : streamer.GephiWS(hostname="localhost", port=8080, workspace="workspace0")
# # You can also use REST call with GephiREST (a little bit slower than Websocket)
# stream = streamer.Streamer(streamer.GephiWS(hostname="localhost", port=8080, workspace="workspace1"))
#
#
# # Create a node with a custom_property
# node_a = graph.Node("A",custom_property=1)
#
# # Create a node and then add the custom_property
# node_b = graph.Node("B")
# node_b.property['custom_property']=2
#
# # Add the node to the stream
# # you can also do it one by one or via a list
#  #l = [node_a,node_b]
#  #stream.add_node(*l)
#
# #stream.add_node(node_a,node_b)
#
# # Create edge
# # You can also use the id of the node : graph.Edge("A","B",custom_property="hello")
# edge_ab = graph.Edge(node_a,node_b,custom_property="hello")
#
# stream.add_edge(edge_ab)
#
# def streamLinks():
#     for y in allUniqueSpheres:
#         node_b = graph.Node(y)
#         stream.add_node(node_b)
#
#     for x in allLinks:
#         edge_ab = graph.Edge(x['source'], x['target'])
#         stream.add_edge(edge_ab)


# import itertools
# from operator import itemgetter
#
# sorted_animals = sorted(allLinks, key=itemgetter('weight'))
# # pprint (sorted_animals)
#
# # G=nx.Graph()
# G = nx.DiGraph()
#
# G.add_nodes_from(allUniqueSpheres)
#
# for x in allLinks:
#     G.add_edge(x['source'], x['target'], weight=x['weight'])
#
# # print G.in_edges('the',data='weight')
#
# with open('mycsvfile.csv', 'wb') as f:  # Just use 'w' mode in 3.x
#     i = 0;
#     for entry in allLinks:
#         entry['id'] = i
#         i += 1
#
#     w = csv.DictWriter(f, allLinks[0].keys())
#     w.writeheader()
#     w.writerows(allLinks)
