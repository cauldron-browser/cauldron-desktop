from bs4 import BeautifulSoup
import urllib.request
import requests 
import gensim
from difflib import SequenceMatcher
from rake_nltk import Rake
import index
from google import search
import random
import numpy as np
import time

def findAllLinks(soup):
    # Gets all the links that are present on a webpage
    #TODO: include the relative links
    #TODO: what to do if the link is an image?

    content = []
    for link in soup.find_all('a', href=True):
        if link['href'].startswith('http'):
            content.append(link['href'])

    return content

def findRelevantLinks(soup):

    all_links = [tag['href'] for tag in soup.select('p a[href]')]
    return all_links


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

def extractKeywords(text):
    # Extracts the most important words from a given text

    r = Rake()
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases() # To get keyword phrases ranked highest to lowest.

def contentSimilarity(mainVector,url, m):

    try:
        resp = urllib.request.urlopen(url)
    except:
        return 0
    soup = BeautifulSoup(resp, 'lxml')
    page = index.parse_html_string(str(soup))


    split = page.content.strip().split()
    vector = m.infer_vector(split, alpha=0.01, steps=1000)


    print("Dot product: %s"%str(np.dot(mainVector/np.linalg.norm(mainVector), vector/np.linalg.norm(vector))))
    return np.dot(mainVector/np.linalg.norm(mainVector), vector/np.linalg.norm(vector))

def selectedWeightedKeyWords(content):

    keywords = extractKeywords(content)
    main = keywords[:5]
    beginning = random.sample(keywords[5:len(keywords)//3],5)
    middle = random.sample(keywords[len(keywords)//3:2*len(keywords)//3],2)
    end = random.sample(keywords[2*len(keywords)//3:],1)

    return main+beginning+middle+end

def selectedKeyWords(content):

    keywords = extractKeywords(content)
    return [np.random.choice(keywords, 2 , replace=False) for i in range(5)]

def googleSearch(page, q):

    keywords = [page.title] + [' '.join(x) for x in selectedKeyWords(page.content)]
    for keyword in keywords:
        results = search(keyword, stop = 5)
        for result in results:
            q.append(result)

def main(url, access_time, query, model, q):

    if query:
        results = search(query, stop = 10)
        for result in results:
            q.append(result)

    try:
        mainResponse = urllib.request.urlopen(url)
    except:
        return

    mainSoup = BeautifulSoup(mainResponse, 'lxml')
    mainPage = index.parse_html_string(str(mainSoup))

    googleSearch(mainPage, q)

    splitDocument = mainPage.content.strip().split()
    mainVector = model.infer_vector(splitDocument, alpha=0.01, steps=1000)

    #firstLevel = random.sample(findAllLinks(mainSoup), 10)



    for link in firstLevel:
        if contentSimilarity(mainVector, link, model) >= .4:
            q.append(link)

'''
mainResponse = urllib.request.urlopen('https://stackoverflow.com/questions/23373471/how-to-find-all-links-in-all-paragraphs-in-beautiful-soup')
mainSoup = BeautifulSoup(mainResponse, 'lxml')

print(findRelevantLinks(mainSoup))
'''