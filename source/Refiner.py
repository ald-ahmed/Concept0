# -*- coding: utf-8 -*-


import requests
import re
import string
from pprint import pprint
from collections import Counter
import globalVars as all
from collections import defaultdict


class Refiner:
    query = ""
    extract = ""
    links = []
    spheres = []
    done = 0

    def __init__(self, word,td):
        self.query = word
        self.getContent(word)
        self.createSpheresFromText()
        self.updatePairs()
        if td:
            self.recreateSpheres()
        self.addToAllSpheres(self.spheres)
        self.createLinks()

    def __del__(self):
        print ''


    def recreateSpheres(self):

        if self.done is 0:
            return
        # print "spheres before: ", self.spheres
        newSubjects = {}
        tempSubject = []
        replaceStarting = -1
        strongConnection = 1
        strengthThreshold = 2
        i = 0
        while strongConnection:
            if len(tempSubject) == 0:
                tempSubject.append(self.spheres[i])
                # print "\n added ", self.spheres[i]

            pairFrequency = all.pairs[tempSubject[len(tempSubject) - 1]][self.spheres[i + 1]]
            strengthMetric = pairFrequency

            # print "strengthMetric is ", strengthMetric , " inversefreq is ", inverseFrequency, "and freq of both is", pairFrequency

            functionalWord = 1

            # if self.spheres[i] in all.functionalChart and self.spheres[i+1] in all.functionalChart:
            #     if all.functionalChart[self.spheres[i]] == -1 or all.functionalChart[self.spheres[i+1]] == -1:
            #         functionalWord = -1

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

    def updatePairs(self):
        if self.done is 0:
            return
        for i in range(len(self.spheres) - 1):
            if self.spheres[i] not in all.pairs:
                all.pairs[self.spheres[i]] = defaultdict(int)
                all.pairs[self.spheres[i]].update({self.spheres[i + 1]: 1})
            else:
                all.pairs[self.spheres[i]][self.spheres[i + 1]] += 1

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

        # count how many non standard characters there are in each word, if 2 or less, add it
        for x in extract:
            x = x.strip(string.punctuation)
            numberOfMatches = len(re.findall(pattern, x))
            if x != '' and numberOfMatches < 3:
                self.spheres.append(x.lower())

        return self.spheres



    def getContent(self, query):

        print "Requesting ", query
        data = requests.get('http://en.wikipedia.org/w/api.php?format=json'
                            '&action=query&prop=extracts&exintro=&explaintext=&titles='
                            + query +
                            '&redirects=1')
        jsonData = data.json()




        try:
            redirectTo= jsonData['query']['redirects'][0]['to']
            redirectTo= redirectTo.lower().strip()
            print "redirects to ", redirectTo
            if redirectTo in all.Spheres:
                if all.Spheres[redirectTo][1]==1:
                    print 'Entry already linked'
                    return -1
            else:
                all.Spheres[redirectTo] = [1,1,1]
                entry = {
                    'source': self.query,
                    'target': redirectTo,
                    'weight': 1
                }
                self.links.append(entry)

        except:
            pass
        try:
            pageNumber = jsonData['query']['pages'].keys()[0]
            if pageNumber == '-1':
                print 'Entry not found'
                return -1
        except:
            return -1


        extract = jsonData['query']['pages'][pageNumber]['extract']

        if "may refer to" in extract or (len(extract) < len(query)+10):
            print 'Entry redirects'
            # print extract
            return -1
        else:
            self.extract = extract.encode('utf-8', 'ignore')
            self.done = 1
            return self.extract

    def deleteAll(self):
        del self.links[:]
        del self.spheres[:]
