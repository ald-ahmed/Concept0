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
import copy
from collections import OrderedDict
from collections import Counter
from itertools import islice
import itertools
import operator
from difflib import SequenceMatcher
import math

G = nx.Graph()

whatsNormalAnyway = []

def average(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def writeLinkToCSV(filename):
    writer = csv.writer(open(filename + ".csv", "wb"))
    i = 0
    writer.writerow(["ID", "Source", "Target", "Weight"])
    for link in all.Links:
        writer.writerow([i, link['source'], link['target'], link['weight']])
        i += 1


def saveVariables():
    pickle.dump(all.Spheres, open("spheres.p", "wb"))
    pickle.dump(all.nonuniquecount, open("nonuniquecount.p", "wb"))
    pickle.dump(all.functionalChart, open("functional.p", "wb"))
    pickle.dump(all.Links, open("links.p", "wb"))


def loadVariables():
    all.Spheres = pickle.load(open("spheres.p", "rb"))
    all.nonuniquecount = pickle.load(open("nonuniquecount.p", "rb"))
    all.functionalChart = pickle.load(open("functional.p", "rb"))
    all.Links = pickle.load(open("links.p", "rb"))


def expand(limit):
    counter = 0
    for sphere in all.Spheres:
        if all.Spheres[sphere][1] == 0:
            counter += 1

    snapShot = copy.deepcopy(all.Spheres)
    current = 0

    for sphere in snapShot:
        if snapShot[sphere][1] == 0:
            explore(sphere, 1, 1)
            current += 1
            print current, "out of ", limit
            if current == limit:
                return


def isFunctional(topic):
    try:
        if all.functionalChart[topic] == -1:
            return 0
        else:
            return 1
    except:
        return 1


def updateNetwork():
    for x in all.Links:
        if isFunctional(x['source']) and isFunctional(x['target']):
            G.add_edge(x['source'], x['target'], weight=x['weight'])


# refines text and aggregates topics
def topicDetector(text):
    helper = Refiner('', '')

    dividedInput1 = helper.sentenceSplitter(text)

    inputText = helper.sentenceCleaner(dividedInput1)

    topics = []
    for sphere in all.Spheres:
        if len(sphere) > 1:
            topics.append(sphere)

    outputText = []
    pointer = 0
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

            # print "search for", bufferString

            if any(x.startswith(bufferString) for x in topics):
                sentence[pointer] = bufferString
                del sentence[pointer + 1]
                print "aggregated ", bufferString, "\n"
            else:
                bufferString = ""
            pointer += 1
        pointer = 0
        outputText.append(sentence)

    return outputText


def significanceValue(input):
    val = all.Spheres[input][0]*all.Spheres[input][2]*1.0
    return val



# given a topic and a theme, return list of distance paths
def topicToThemeDistance(topic, theme):

    result = []

    if nx.has_path(G, source=topic, target=theme):
        paths = k_shortest_paths(G, topic, theme, 10)
        pprint(paths)
        for path in paths:
            result.append(minimumEffectiveDistance(path))

    return result


def minimumEffectiveDistance(path):

    rarityListDistance = []

    if len(path) < 3:
        return 0

    for i, sharedNode in enumerate(path):
        if i != len(path) - 1:
            prevalence = significanceValue(sharedNode)
            rarityListDistance.append(prevalence)

    distanceAvg = average(rarityListDistance) * math.pow(len(path), 3)

    return distanceAvg


def summarize(text, theme, depth):
    updateNetwork()

    helper = Refiner('', '')

    dividedInput1 = helper.sentenceSplitter(text)

    print "\n"

    outputText = topicDetector(text)

    if theme not in G:
        print "theme", theme, "not in network"
        explore(theme, depth, 1)
        updateNetwork()

    relevancyList = []

    for sentence in outputText:
        print "\n\n\nSENTENCE ", sentence, "\n\n"

        numberOfWordsDetected = 0
        totalDistance = 0
        consideredWords = len(sentence)
        for item in sentence:
            item = "".join(item).lower()
            # print "item: ", item

            if not isFunctional(item):
                consideredWords -= 1
                continue

            if item not in all.Spheres:
                continue
                # print "did not find ", item
                explore(item, depth, 1)
                updateNetwork()
                # saveVariables()

            if item not in G:
                print item, " not in G"
                continue

            # returns list of possible topic alternatives
            possibleAlt = findSimilarTopic(item)

            altDistances = []
            for alter in possibleAlt:
                altDistances.append(average(topicToThemeDistance(alter, theme)) / all.nonuniquecount)

            print altDistances

            # distance is smallest out of all possible alternatives and original
            minOuter = min(altDistances)

            sigVal = significanceValue(item)

            print "\n\n\n\n",item,sigVal
            minOuter = minOuter

            totalDistance += minOuter
            numberOfWordsDetected += 1
            print "\t\t final - > ", minOuter

        print "\n"
        if numberOfWordsDetected == 0:
            numberOfWordsDetected = 1
        relevancyList.append(
            [totalDistance / (numberOfWordsDetected * 1.0), (numberOfWordsDetected * 1.0 / consideredWords * 1.0)])


    mean = average([x[0] for x in relevancyList])
    meanMeasured = average([x[1] for x in relevancyList]) * 100
    std = np.std([x[0] for x in relevancyList])
    zscore = [abs(x[0] - mean) / std for x in relevancyList]

    print '{:^20}{:^20}{:^20}{:^20}'.format("sentence", "common", "% measured", "z-score")

    for i, item in enumerate(relevancyList):
        print '{:^20}{:^20.5}{:^20.5}{:^20.5}'.format(i + 1, item[0], item[1] * 100, zscore[i])

    print "\nmean distance: ", mean
    print "mean % words connected: ", meanMeasured
    print "standard deviation: ", std


    if meanMeasured < 50:
        expand(50)
        summarize(text, theme, depth)
        return ()

    print "\n\n\n Original:\n"

    i = 1
    for x in dividedInput1:
        print i,
        i += 1
        for y in x:
            print y,

    print "\n\n\n Summary:\n"

    meanList = []

    for i, item in enumerate(relevancyList):
        meanList.append(item[0])

    Y = np.array(meanList).reshape((len(meanList), 1))
    Y = StandardScaler().fit_transform(Y)

    db = DBSCAN(min_samples=len(relevancyList) * .5)
    db.fit(Y)

    limit = mean - (0.5 * std)

    for index, sentence in enumerate(relevancyList):
        if relevancyList[index][0] < limit:
            print " ".join(dividedInput1[index]),

    print "\n\n\n"

    for index, sentence in enumerate(relevancyList):
        if relevancyList[index][0] > limit:
            # print relevancyList[index], index
            print "- Deleted [", " ".join(dividedInput1[index]), "]"

    print "\n\n"

    for index, sentence in enumerate(relevancyList):
        if db.labels_[index] != -1:
            print " ".join(dividedInput1[index]),

    print "\n\n\n"

    for index, sentence in enumerate(relevancyList):
        if db.labels_[index] == -1:
            print "- Deleted [", " ".join(dividedInput1[index]), "]"

            # for x in outputText:
            #     print(x)


def printPairs():
    for word in all.pairs:
        print "\n", word, ": \n"
        for child in all.pairs[word]:
            print "{:>20}{: ^10} ".format(child, all.pairs[word][child])


def unsupervisedMagic():
    X = []
    Y = []

    # for index, word in enumerate(all.Spheres):
    #     freq = ((all.Spheres[word][0] * 1.0) / all.nonuniquecount)
    #     spread = all.Spheres[word][2]
    #     X.append(index)
    #     Y.append(freq * spread)

    numberToFit = len(all.Spheres) / 100

    for i in range(numberToFit):
        print i, "/", numberToFit

        word = all.Spheres.keys()[i]
        freq = ((all.Spheres[word][0] * 1.0) / all.nonuniquecount)
        spread = all.Spheres[word][2]
        Y.append(freq * spread)

    Y = np.array(Y).reshape((len(Y), 1))
    Y = StandardScaler().fit_transform(Y)

    db = DBSCAN(eps=0.2, min_samples=10)
    db.fit(Y)

    # pl.figure('functional vs non-functional words')
    # pl.scatter(X, Y, s=50, c=db.labels_)

    mark = -1

    for index in range(len(db.labels_)):

        all.functionalChart[all.Spheres.items()[index][0]] = db.labels_[index]

        if all.functionalChart[all.Spheres.items()[index][0]] == -1:
            mark = time.time()
            print "non functional word -> ", all.Spheres.items()[index][0]

            # pl.annotate(word.decode(encoding='UTF-8'), xy=(X[index], Y[index]))

            # pl.show()

        if mark != -1:
            duration = time.time() - mark
            print "time since last non-func", duration

            if duration > 300:
                print "its been too long since last reported non-functional word, timing out"
                return


# start at what, end at what, and 1 or 0 for topic detection
def explore(word, length, td):
    if word in all.Spheres:
        if all.Spheres[word][1] == 1:
            print "\t\t\tquery been linked ->", word
            return
        else:
            print "\t\t\tquery not yet linked ->", word
            del all.Spheres[word]

    all.Spheres[word] = [1, 0, 1]

    i = len(all.Spheres) - 1
    length = i + length - 1

    while len(all.Spheres) > 0:
        print i

        try:
            query = all.Spheres.keys()[i]
        except:
            print "\t\t\t\t\t\t\t\tNo spheres to explore, dead end."
            break

        newWord = Refiner(query, td)

        if newWord.done is 1:
            if all.Spheres[newWord.links[0]['source']][1] != 1:
                all.Links.extend(newWord.links)
                all.Spheres[newWord.links[0]['source']][1] = 1
        else:
            all.Spheres[query][1] = 1

        newWord.deleteAll()

        if i != length:
            i += 1
        else:
            break;


def feedCorpus():
    for i in range(1):
        from bs4 import BeautifulSoup, SoupStrainer
        import re

        f = open('reut2-00' + str(i) + '.sgm', 'r')
        data = f.read()
        soup = BeautifulSoup(data, "html.parser")
        contents = soup.findAll('body')

        corpus = ""
        for content in contents:
            sentence = content.text
            sentence = re.sub(r"\s+", " ", sentence, flags=re.UNICODE)
            sentence = re.sub(r"Reuter", "", sentence, re.IGNORECASE)
            sentence = re.sub(r"REUTER", "", sentence, re.IGNORECASE)
            sentence = sentence.replace(">", "")
            sentence = sentence.replace("<", "")

            corpus += sentence + " "
        corpus = corpus.encode('utf-8', 'ignore')
        corpus = corpus.replace("  ", "")
        newWord = Refiner(corpus, 1)


def prepResearch(text):
    text = topicDetector(text)
    newText = []

    for sentence in text:
        for word in sentence:
            newText.append(word)

    frequencies = Counter(newText)
    importantWords = OrderedDict()

    for i, x in enumerate(sorted(frequencies.values())):
        if isFunctional(frequencies.keys()[i].lower()):
            importantWords[frequencies.keys()[i]] = frequencies.values()[i]
    finalList = []
    avg = (average(importantWords.values()))
    for topic in importantWords:
        if importantWords[topic] > avg:
            finalList.append(topic)

    pprint(finalList)

    for topic in finalList:
        explore(topic, 1, 1)


def k_shortest_paths(G, source, target, k, weight=None):
    return list(islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))


def complete_graph_from_list(L, create_using=G):
    G = nx.empty_graph(len(L), create_using)
    if len(L) > 1:
        if G.is_directed():
            edges = itertools.permutations(L, 2)
        else:
            edges = itertools.combinations(L, 2)
        G.add_edges_from(edges)
    return G


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def findSimilarTopic(input):
    result = [input]

    if input not in G:
        return result
    list1 = [p for p in nx.all_neighbors(G, input)]
    max = -1
    close = ""

    for n in list1:
        count = similar(n, input)
        if count > max or max == -1:
            max = count
            close = n
    if max > 0.7:
        result.append(close)
        print input, "->", close

    return result


t1 = time.time()

all.init()

all.functionalChart = pickle.load(open("functional.p", "rb"))

# feedCorpus()
# unsupervisedMagic()

#
# #loadVariables()
#
#
#
parameter = 'Hillary Clinton thanked her supporters, referring to her popular-vote victory, and wished them a happy holiday season in an end-of-year email sent Monday. In the email, Clinton mentioned the rough number of votes she received in the 2016 presidential election and that her popular vote win showed promise. But she did not indicate any specific plans for the future. The email ended with Clintons well wishes for the new year and said she would be "in touch" in 2017. She also expressed her year-end wishes on Twitter. Hillary Clinton is an American politician and previous U.S senator from New York. Elephants can fly very high. Clinton lost the presidential nomination in 2016.'

# parameter ="Hillary Clinton is a previous senator. Computers are cool."
# parameter = "On February 10, 2007, Obama announced his candidacy for President of the United States in front of the Old State Capitol building in Springfield, Illinois. The choice of the announcement site was viewed as symbolic because it was also where Abraham Lincoln delivered his historic 'House Divided' speech in 1858. Obama emphasized issues of rapidly ending the Iraq War, increasing energy independence, and reforming the health care system, in a campaign that projected themes of hope and change."

# parameter = "On April 12, 2015, Clinton formally announced her candidacy for the presidency in the 2016 election. She had a campaign-in-waiting already in place, including a large donor network, experienced operatives, and the Ready for Hillary and Priorities USA Action political action committees, and other infrastructure. The campaign's headquarters were established in the New York City borough of Brooklyn. Focuses of her campaign have included raising middle class incomes, establishing universal preschool and making college more affordable, and improving the Affordable Care act. Initially considered a prohibitive favorite to win the Democratic nomination, Clinton faced an unexpectedly strong challenge from self-professed democratic socialist Senator Bernie Sanders of Vermont, whose longtime stance against the influence of corporations and the wealthy in American politics resonated with a dissatisfied citizenry troubled by the effects of income inequality in the U.S. and contrasted with Clinton's Wall Street ties."


#
#
# parameter=""
# f = open( "ps.txt", "r" )
# for line in f:
#     parameter += line.decode('utf-8').encode('ascii',errors='ignore')

parameter = parameter.replace("-", " ")
#
#


# for word in parameter.split():
#    print "\t\t\t\t\t\t\t\tsending ", word.strip(string.punctuation).lower(), "to explore"
#    explore(word.strip(string.punctuation).lower(),2,1)


loadVariables()

# explore("hillary clinton",2,1)



#
# while 1:
#     t2 = time.time()
#     if t2-t1 > (60*60*10):
#         break
#     try:
#         expand(500)
#         saveVariables()
#     except:
#         pass
#
#

# unsupervisedMagic()




#
#

#
# #prepResearch(parameter)
#
#



updateNetwork()

#
# d= []
# count = {}
#
# for sentence in text:
#     for topic in sentence:
#         if topic not in G or not isFunctional(topic):
#             continue
#         list1 = [p for p in nx.all_neighbors(G,topic)]
#
#         list2=[]
#         for neighbor in list1:
#             list2.extend([p for p in nx.all_neighbors(G,neighbor)])
#         list1.extend(list2)
#
#         d.append(list1)
#
#         for word in list1:
#             if word in count:
#                 count[word]+=1
#             else:
#                 count[word]=1
#
#
# for entry in count.keys():
#     prevalency = (all.Spheres[entry][0])
#     count[entry] = count[entry]*(1.0/prevalency)
#
# sorted_x = sorted(count.items(), key=operator.itemgetter(1))
# pprint(sorted_x)
#
# print list(reduce(set.intersection, [set(item) for item in d ]))


# for word in all.Spheres:
#     whatsNormalAnyway.append(all.Spheres[word][0] * all.Spheres[word][2] * 1.0)
#
# print math.log(whatsNormalAnyway[0])


summarize(parameter,'election',2)


t2 = time.time()
print "\n\n\n"
print "\t\t\t\ttime: ", t2 - t1
print "\t\t\t\t", len(all.Spheres), " words collected"
print "\t\t\t\t", len(all.pairs), " pairs made"
print "\t\t\t\t", len(all.Links), " links made"
