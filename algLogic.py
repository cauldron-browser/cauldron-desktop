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

def extractKeywords(text):
    # Extracts the most important words from a given text

    r = Rake()
    r.extract_keywords_from_text(text)
    return r.get_ranked_phrases() # To get keyword phrases ranked highest to lowest.

def contentSimilarity(url1,url2):
    #TODO: given two pages/soups/sets of keywords, evaluates how similar/mutually relevant their content
    resp1 = urllib.request.urlopen(url1)
    soup1 = BeautifulSoup(resp1, 'lxml')
    page1 = index.parse_html_string(str(soup1))

    resp2 = urllib.request.urlopen(url2)
    soup2 = BeautifulSoup(resp2, 'lxml')
    page2 = index.parse_html_string(str(soup2))

    website_documents = [page1.content, page2.content]
    website_documents_split = [x.strip().split() for x in website_documents]

    website_vecs = [m.infer_vector(d, alpha=0.01, steps=1000) for d in website_documents_split]
    vec1 = website_vecs[0]
    vec2 = website_vecs[1]
    #print(np.dot(vec1/np.linalg.norm(vec1), vec2/np.linalg.norm(vec2)))
    return None

def selectedKeyWords(content):

    keywords = extractKeywords(content)
    main = keywords[:5]
    beginning = random.sample(keywords[5:len(keywords)//3],5)
    middle = random.sample(keywords[len(keywords)//3:2*len(keywords)//3],2)
    end = random.sample(keywords[2*len(keywords)//3:],1)
    return main+beginning+middle+end

def googleSearch(url):

    resp = urllib.request.urlopen(url)
    soup = BeautifulSoup(resp, 'lxml')
    page = index.parse_html_string(str(soup))
    keywords = [page.title] + selectedKeyWords(page.content)
    counter = 0
    for keyword in keywords:
        results = search(keyword, stop = 5)
        for result in results:
            r = requests.post("http://127.0.0.1:8091/visit", data={'url': result})

m = gensim.models.Doc2Vec.load("doc2vec.bin")
