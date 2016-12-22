from Refiner import Refiner
from pprint import pprint
import time
from wiktionaryparser import WiktionaryParser
import globalVars as all
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import pylab as pl
import csv
import cPickle as pickle

allLinks = []  # all the source - target - weight links that have been created


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def writeLinkToCSV(filename):
    writer = csv.writer(open(filename + ".csv", "wb"))
    i = 0
    writer.writerow(["ID", "Source", "Target", "Weight"])
    for link in allLinks:
        writer.writerow([i, link['source'], link['target'], link['weight']])
        i += 1


def saveVariables():
    pickle.dump(all.Spheres, open("spheres.p", "wb"))
    pickle.dump(all.nonuniquecount, open("nonuniquecount.p", "wb"))


def loadVariables():
    all.Spheres = pickle.load(open("spheres.p", "rb"))
    all.nonuniquecount = pickle.load(open("nonuniquecount.p", "rb"))


def printPairs():
    for word in all.pairs:
        print "\n", word, ": \n"
        for child in all.pairs[word]:
            print "{:>20}{: ^10} ".format(child, all.pairs[word][child])


def grabPartOfSpeech(word):
    print word, " is a "
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

    parser = WiktionaryParser()
    word = parser.fetch(word)
    result = []
    if len(word) > 0:
        for entry in word[0]['definitions']:
            result.append(entry['partOfSpeech'])
    print result
    return result


def unsupervisedMagic():
    X = []
    Y = []

    for index, word in enumerate(all.Spheres):
        freq = ((all.Spheres[word][0] * 1.0) / all.nonuniquecount)
        spread = all.Spheres[word][2]
        X.append(index)
        Y.append(freq * spread)

    Y = np.array(Y).reshape((len(Y), 1))
    Y = StandardScaler().fit_transform(Y)

    db = DBSCAN(eps=0.2, min_samples=10)
    db.fit(Y)

    # pl.figure('functional vs non-functional words')
    # pl.scatter(X, Y, s=50, c=db.labels_)


    for index in range(len(db.labels_)):
        all.functionalChart[all.Spheres.items()[index][0]] = db.labels_[index]
        #if db.labels_[index] == -1:
           #print "non functional word -> ", all.Spheres.items()[index][0]

            # pl.annotate(word.decode(encoding='UTF-8'), xy=(X[index], Y[index]))
            # pl.show()


# start at what, end at what, and 1 or 0 for topic detection
def searchTree(i, length, td):
    query = all.Spheres.keys()[i]

    newWord = Refiner(query, td)
    print i
    if newWord.done is 1:
        if all.Spheres[newWord.links[0]['source']][1] != 1:
            allLinks.extend(newWord.links)
            all.Spheres[newWord.links[0]['source']][1] = 0
    else:
        all.Spheres[query][1] = 1

    newWord.deleteAll()

    if i != length:
        return searchTree(i + 1, length, td)
    else:
        return i


def runner():
    keepGoing = 1
    all.Spheres['middle east'] = [1, 0, 0]
    counter = 0
    while keepGoing:
        counter = searchTree(counter, (counter + 300), 0)
        saveVariables()
        unsupervisedMagic()

        if "was" in all.functionalChart:
            if all.functionalChart["was"] == -1:
                keepGoing = 0


t1 = time.time()

all.init()

try:
    loadVariables()
    print "Previously saved data loaded."
    #print len(all.Spheres)
    #runner()
    #saveVariables()

except (OSError, IOError) as e:
    print "No previously saved data found."
    runner()
    saveVariables()

unsupervisedMagic()

all.reset()

all.Spheres['U.S state'] = [1, 0, 1]
searchTree(len(all.Spheres) - 1, len(all.Spheres) + 2, 1)

all.Spheres['iraq'] = [1, 0, 1]
searchTree(len(all.Spheres) - 1, len(all.Spheres) + 2, 1)

writeLinkToCSV('links')

t2 = time.time()
print "time: ", t2 - t1
print len(all.Spheres)


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
