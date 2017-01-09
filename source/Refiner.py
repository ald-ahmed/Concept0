# -*- coding: utf-8 -*-


import requests
import re
import string
from pprint import pprint
from collections import Counter
import globalVars as all
from collections import defaultdict
import copy

class Refiner:
    query = ""
    extract = ""
    links = []
    spheres = []
    done = 0

    def __init__(self, word,td):

        self.query = word
        self.getContent(word)
        if self.done is 0:
            return
        self.createSpheresFromText()
        self.updatePairs()
        if td:
            self.recreateSpheres()
        self.addToAllSpheres(self.spheres)
        self.createLinks()

    def recreateSpheres(self):

        # print "spheres before: ", self.spheres
        newSubjects = {}
        tempSubject = []
        replaceStarting = -1
        strongConnection = 1
        strengthThreshold = 1
        i = 0
        while strongConnection:
            if len(tempSubject) == 0:
                tempSubject.append(self.spheres[i])
                # print "\n added ", self.spheres[i]


            lastWordinBuffer = tempSubject[len(tempSubject) - 1]

            if lastWordinBuffer not in all.pairs:
                pairFrequency=0
            else:
                pairFrequency = all.pairs[lastWordinBuffer][self.spheres[i + 1]]

            strengthMetric = pairFrequency

            functionalWord = 1


            if self.spheres[i] in all.functionalChart:
                functionalWord = all.functionalChart[self.spheres[i]]

            if strengthMetric > strengthThreshold and functionalWord>-1:
                # print "connection is strong between ", tempSubject[len(tempSubject) - 1], " and ", self.spheres[i + 1]
                tempSubject.append(self.spheres[i + 1])
                if replaceStarting is -1:
                    replaceStarting = i
                    # print "temp subject is now ", tempSubject
            else:
                if (tempSubject[len(tempSubject) - 1]) in all.functionalChart:
                    if all.functionalChart[(tempSubject[len(tempSubject) - 1])] == -1:
                        tempSubject.pop(len(tempSubject) - 1)
                # print "connection is weak between ", tempSubject[len(tempSubject) - 1], " and ", self.spheres[i + 1]
                if len(tempSubject) > 1:
                    # print "declaring as a thing: ", " ".join(tempSubject)
                    newSubjects[" ".join(tempSubject)] = 1
                    # print "now deleting " ,replaceStarting, i
                    for x in range(i, replaceStarting - 1, -1):
                        # print "deleting " ,self.spheres[x]
                        self.spheres.pop(x)
                    # print "inserting new thing at ", replaceStarting
                    self.spheres.insert(replaceStarting, " ".join(tempSubject))
                    i = replaceStarting
                replaceStarting = -1
                tempSubject = []
            i += 1
            if i >= len(self.spheres) - 1:
                strongConnection = 0

        #print "spheres after: ", self.spheres
        pprint(newSubjects)


    def sentenceSplitter(self,text):
        result = []
        listOfWords = text.split()
        #print listOfWords
        # quit()
        start = 0
        for index, word in enumerate(listOfWords):
            listOfWords[index] = word
            if word.endswith('.'):
                if word.count('.') > 1:
                    listOfWords[index] = listOfWords[index].replace(".",'')
                    continue

                if word[0].isupper() and len(word.strip(".")) < 4:

                    #print "join them" , word
                    try:
                        listOfWords[index] = listOfWords[index + 1]
                        del listOfWords[index + 1]
                    except:
                        pass
                else:
                    #print "end of sentence" , word
                    result.append(listOfWords[start:index + 1])
                    start = index + 1
        listOfWords[index] = word

        return result

    def sentenceCleaner(self,input):

        text = copy.deepcopy(input)

        for index1, sentence in enumerate(text):
            for index, word in enumerate(sentence):
                word = word.lower().strip(".").strip(string.punctuation).replace(',','')
                sentence[index] = word
            text[index1] = sentence
        result = text

        return result


    def updatePairs(self):
        if self.done is 0:
            return

        splitSentences = self.sentenceCleaner(self.sentenceSplitter(self.extract))

        for sentence in splitSentences:
            for i in range(len(sentence)-1):
                if sentence[i] not in all.pairs:
                    all.pairs[sentence[i]] = defaultdict(int)
                    all.pairs[sentence[i]].update({sentence[i + 1]: 1})
                else:
                    all.pairs[sentence[i]][sentence[i + 1]] += 1

    def createLinks(self):

        listGrouped = Counter(self.spheres)

        for z in listGrouped:
            if z == self.query:
                continue
            entry = {
                'source': self.query,
                'target': z,
                'weight': listGrouped[z]
            }
            self.links.append(entry)

        return self.links

    def addToAllSpheres(self, list):
        newSphereUpdateSpread = {}
        for newSphere in list:
            all.nonuniquecount += 1
            if newSphere in all.Spheres:

                all.Spheres[newSphere][0] += 1
                if newSphere not in newSphereUpdateSpread:
                    all.Spheres[newSphere][2] += 1
                    newSphereUpdateSpread[newSphere]=1
            else:
                all.Spheres[newSphere] = [1, 0, 1]

    def createSpheresFromText(self):
        #print self.extract
        extract = self.extract.replace('—', ' ')

        regex = "[^\w ]"
        pattern = re.compile(regex, re.UNICODE)

        extract = extract.split()

        # count how many non-standard characters there are in each word, if 2 or less, add it
        for x in extract:
            x = x.strip(string.punctuation)
            numberOfMatches = len(re.findall(pattern, x))
            if x != '' and numberOfMatches < 3:
                self.spheres.append(x.lower())

        return self.spheres

    def getContent(self, query):
        if query=='':
            return

        print "\nRequesting ", query
        data = requests.get('http://en.wikipedia.org/w/api.php?format=json'
                            '&action=query&prop=extracts&exintro=&explaintext=&titles='
                            + query +
                            '&redirects=1')
        jsonData = data.json()

        self.caseHandler(jsonData, query)

        return self.extract


    def caseHandler(self,jsonData,query):


        # ENTRY NOT FOUND
        pageNumber = jsonData['query']['pages'].keys()[0]

        if pageNumber == '-1':
            print 'Entry not found'
            all.Spheres[query][1] = 1
            return



        # ENTRY AMBIGUOUS
        extract = jsonData['query']['pages'][pageNumber]['extract']
        self.extract = extract.encode('utf-8', 'ignore')

        if "may refer to" in extract or (len(extract) < len(query) + 10):
            print 'Entry is ambiguous'
            all.Spheres[query][1] = 1
            return

        # ENTRY REDIRECTS
        try:
            redirectTo = jsonData['query']['redirects'][0]['to']
            redirectTo = redirectTo.lower().strip().encode('utf-8', 'ignore')

            if redirectTo!=query:
                print "redirects to " + redirectTo

                if redirectTo in all.Spheres:
                    print 'Entry already/will be linked'
                    all.Spheres[query][1] = 1
                    return
                else:
                    all.Spheres[redirectTo] = [1, 0, 1]
                    entry = {
                        'source': query,
                        'target': redirectTo,
                        'weight': 1
                    }
                    all.Links.append(entry)
                    all.Spheres[query][1] = 1
                    print "linked", query, "and", redirectTo
                    return
        except:
            pass

        self.done = 1

    def deleteAll(self):
        del self.links[:]
        del self.spheres[:]
