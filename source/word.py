# -*- coding: utf-8 -*-


import requests
import re
import string
from collections import Counter


class Word:
    query = ""
    extract = ""
    links = []
    spheres = []

    def __init__(self, word):
        self.query = word
        self.getContent(word)
        self.createSpheresFromText()
        self.createLinks()

    def __del__(self):
        print self.query, ' ended'

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

    def createSpheresFromText(self):

        extract = self.extract.replace('—', ' ')

        regex = r"[^\w ]"
        pattern = re.compile(regex, re.UNICODE)

        extract = extract.split()

        for x in extract:
            x = x.strip(string.punctuation)
            numberOfMatches = len(re.findall(pattern, x))
            if x != '' and numberOfMatches < 2:
                self.spheres.append(x.lower())
        return self.spheres

    def getContent(self, query):
        print "Requesting " , query
        data = requests.get('http://en.wikipedia.org/w/api.php?format=json'
                            '&action=query&prop=extracts&exintro=&explaintext=&titles='
                            + query +
                            '&redirects=1')
        jsonData = data.json()
        #print jsonData

        pageNumber = jsonData['query']['pages'].keys()[0]

        if pageNumber == '-1':
            print 'Entry not found'
            return -1

        extract = jsonData['query']['pages'][pageNumber]['extract']

        if "may refer to" in extract:
            if len(extract)<20:
                print 'Entry redirects'
                print extract
                return -1
        else:
            self.extract = extract.encode('utf-8', 'ignore')
            return self.extract

    def getLinks(self):
        return self.links

    def deleteAll(self):
        del self.links[:]
        del self.spheres[:]


