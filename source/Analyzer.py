from Refiner import Refiner
from pprint import pprint
import time
import globalVars as all
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import pylab as pl
import csv
import cPickle as pickle
import networkx as nx
import re
import string

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
    pickle.dump(all.functionalChart, open("functional.p", "wb"))


def loadVariables():
    all.Spheres = pickle.load(open("spheres.p", "rb"))
    all.nonuniquecount = pickle.load(open("nonuniquecount.p", "rb"))
    all.functionalChart = pickle.load(open("functional.p", "rb"))


def printPairs():
    for word in all.pairs:
        print "\n", word, ": \n"
        for child in all.pairs[word]:
            print "{:>20}{: ^10} ".format(child, all.pairs[word][child])


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
        # if db.labels_[index] == -1:
        # print "non functional word -> ", all.Spheres.items()[index][0]
        # pl.annotate(word.decode(encoding='UTF-8'), xy=(X[index], Y[index]))

        # pl.show()


# start at what, end at what, and 1 or 0 for topic detection
def searchTree(i, length, td):
    try:
        query = all.Spheres.keys()[i]
    except:
        print "                                     ran into a dead end!"
        return i

    newWord = Refiner(query, td)
    print i
    if newWord.done is 1:
        if all.Spheres[newWord.links[0]['source']][1] != 1:
            allLinks.extend(newWord.links)
            all.Spheres[newWord.links[0]['source']][1] = 1
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
    print "Loaded ", len(all.Spheres), "spheres. \n"

except (OSError, IOError) as e:
    print "No previously saved data found."
    runner()
    unsupervisedMagic()
    saveVariables()



# all.reset()
#
#
# all.Spheres['united states'] = [1, 0, 1]
# searchTree(len(all.Spheres) -1, len(all.Spheres)+50, 1)
#
# all.Spheres['elephant'] = [1, 0, 1]
# searchTree(len(all.Spheres) -1, len(all.Spheres)+20, 1)
#
#
# all.Spheres['hillary clinton'] = [1, 0, 1]
# searchTree(len(all.Spheres) -1, len(all.Spheres)+50, 1)
#
# all.Spheres['donald trump'] = [1, 0, 1]
# searchTree(len(all.Spheres) -1, len(all.Spheres)+50, 1)
#
# all.Spheres['obama'] = [1, 0, 1]
# searchTree(len(all.Spheres) -1, len(all.Spheres)+50, 1)
#
# writeLinkToCSV('linksOG1')
#
# t2 = time.time()
# print "\t\t\t\ttime: ", t2 - t1
# print "\t\t\t\t", len(all.Spheres), " words collected"
# saveVariables()
# pickle.dump(allLinks, open("links.p", "wb"))
#



allLinks = pickle.load(open("links.p", "rb"))

inputText = 'Hillary Clinton thanked her supporters, referring to her popular-vote victory, and wished them a happy holiday season in an end-of-year email sent Monday. In the email, Clinton mentioned the rough number of votes she received in the 2016 presidential election and that her popular vote win showed promise. But she did not indicate any specific plans for the future. The email ended with Clintons well wishes for the new year and said she would be "in touch" in 2017. She also expressed her year-end wishes on Twitter. Hillary Clinton is an American politician and previous U.S senator from New York. Elephants can fly very high. Clinton lost the presidential nomination in 2016.'

#
# inputText=""
# f = open( "article.txt", "r" )
# for line in f:
#     inputText += line.decode('utf-8').encode('ascii',errors='ignore')


def sentenceSplitter(text):
    result=[]
    listOfWords = text.split()

    start=0
    for index, word in enumerate(listOfWords):
        listOfWords[index] = word.lower().strip(".").strip(string.punctuation)
        if word.endswith('.'):

            print word
            if word.count('.')>1:
                listOfWords[index]= listOfWords[index].replace(".","")
                continue

            if word[0].isupper() and len(word)<4:
                listOfWords[index] = listOfWords[index + 1].lower().strip(".").strip(string.punctuation)
                del listOfWords[index + 1]
            else:
                result.append(listOfWords[start:index+1])
                start = index+1
    listOfWords[index]= word

    return result

inputText= sentenceSplitter(inputText)

pprint(inputText)



topics = []
for sphere in all.Spheres:
    if len(sphere) > 1:
        topics.append(sphere)

outputText = []
pointer = 0
topicPointer = 0
bufferString = ""

for sentence in inputText:

    while pointer < len(sentence) - 1:

        wordAtIndex = sentence[pointer]
        wordAtIndexPlusOne = sentence[pointer + 1]

        topic = wordAtIndex + " " + wordAtIndexPlusOne

        if len(bufferString) == 0:
            bufferString += topic
            # print "buffer is ", bufferString
        else:
            bufferString += " " + wordAtIndexPlusOne

        #print "search for", bufferString

        if any(x.startswith(bufferString) for x in topics):
            sentence[pointer] = [bufferString]
            del sentence[pointer + 1]
            #print "aggregated ", bufferString,"\n"
        else:
            bufferString = ""
        pointer += 1
    pointer = 0
    outputText.append(sentence)

G = nx.Graph()
G = nx.Graph()

for x in allLinks:
    G.add_edge(x['source'], x['target'], weight=x['weight'])


relevancyList = []

for sentence in outputText:
    #print "sentence ",sentence

    numberOfWordsDetected = 0
    totalDistance = 0

    for item in sentence:
        item = "".join(item).lower()
        #print "item: ", item

        if item not in G:
            #print "did not find ", item
            # all.Spheres[item] = [1, 0, 1]
            # searchTree(len(all.Spheres) -1, len(all.Spheres)-1, 1)
            # for x in allLinks:
            #     G.add_edge(x['source'], x['target'], weight=x['weight'])
            # saveVariables()
            # pickle.dump(allLinks, open("links.p", "wb"))
            continue
        if len(item) < 2:
            if all.functionalChart[item] != -1:
                continue

        if nx.has_path(G, source=item, target='politics'):
            path = ([p for p in nx.shortest_path(G, source=item, target='politics')])
            # print path
            totalDistance += len(path)
            numberOfWordsDetected += 1

    relevancyList.append([totalDistance / (numberOfWordsDetected * 1.0), (numberOfWordsDetected * 1.0 / len(sentence) * 1.0)])
    numberOfWordsDetected = 0
    totalDistance = 0

pprint(relevancyList)

mean = mean([x[0] for x in relevancyList])
std = np.std([x[0] for x in relevancyList])
zscore = [abs(x[0] - mean) / std for x in relevancyList]

print "\nmean: ", mean
print std
pprint(zscore)

print "\n\n\n Original:\n"


flatInput = []
for sentence in inputText:
    inputTextFlat = []
    for word in sentence:
        if len(word[0])!=1:
            inputTextFlat.extend(word)
        else:
            inputTextFlat.append(word)
    flatInput.append(inputTextFlat)

for sentence in flatInput:
    print " ".join(sentence)+ ".",

print "\n\n\n Summary:\n"

limit = mean-(0.1*std)

for index, sentence in enumerate(relevancyList):
    if relevancyList[index][0] < limit:
        print " ".join(flatInput[index])+".",

print "\n\n\n"

for index, sentence in enumerate(relevancyList):
    if relevancyList[index][0] > limit:
        #print relevancyList[index], index
        print "- Deleted [",  " ".join(flatInput[index])+".", "]"
