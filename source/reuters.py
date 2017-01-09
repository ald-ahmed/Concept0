from bs4 import BeautifulSoup,SoupStrainer



f = open('r.sgm', 'r')
data= f.read()
soup = BeautifulSoup(data)
contents = soup.findAll('content')
for content in contents:
    print content.text