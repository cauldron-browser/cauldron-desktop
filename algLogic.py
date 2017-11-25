from bs4 import BeautifulSoup
import urllib.request
import gensim
from difflib import SequenceMatcher
from rake_nltk import Rake



def findAllLinks(url):
    # Gets all the links that are present on a webpage
    resp = urllib.request.urlopen(url)
    soup = BeautifulSoup(resp, 'lxml')

    content = []
    for link in soup.find_all('a', href=True):
        if link['href'].startswith('http'):
            content.append(link['href'])
    return content

def checkURL(url, setOfPages):
    # Checks if a given url is in the set setOfPages
    return url in setOfPages

def findMetaData(soup):
    # Scrapes a website and returns a list with the contents of each meta tag

    contents = []
    for tag in soup.find_all('meta'):
        contents.append(tag['content'])
    return contents

def similar(a, b):
    # Returns a number from zero to one of how similar two strings are
    return SequenceMatcher(None, a, b).ratio()

def simpleContentSimilarity(soupPage1, soupPage2):
    # Given two soups, returns a value (unbounded?) of how similar the pages are
    meta1 = ''.join(findMetaData(soupPage1))
    meta2 = ''.join(findMetaData(soupPage2))

    print(type(meta1))
    print(len(meta2))
    return similar(meta1,meta2)

def contentSimilarity(soupPage1,soupPage2):
    r = Rake()
    r.extract_keywords_from_text(<text to process>)
    r.get_ranked_phrases() # To get keyword phrases ranked highest to lowest.

    meta1 = ''.join(str(elem) for elem in findMetaData(soupPage1))
    meta2 = ''.join(str(elem) for elem in findMetaData(soupPage2))

    website_documents = [meta1, meta2]
    website_documents_split = [x.strip().split() for x in website_documents]
    m = gensim.models.Doc2Vec.load("word2vec.bin")
    website_vecs = [m.infer_vector(d, alpha=0.01, steps=1000) for d in website_documents_split]
    return "yes"

'''
def main(page, savedPages):
    
    if checkURL(page, savedPages):
        #page.relevance = #updated value
    else:
        savedPages.add(page)

        respReference = urllib.request.urlopen(page.url)
        soupReference = BeautifulSoup(resp, 'lxml')

        for link in crawler.findAllLinks(page.url):

            resp = urllib.request.urlopen(link)
            soup = BeautifulSoup(resp, 'lxml')
            
            if contentSimilarity(soupReference, soup2) >= similarityThreshold:
                #downloadPage(link)
'''