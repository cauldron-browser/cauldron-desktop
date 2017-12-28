#!/usr/bin/env python

import argparse
from collections import deque
from multiprocessing import Queue
import os
import subprocess
import sys
import time
import threading
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, send_from_directory
import gensim
import google
import signal
from sqlitedict import SqliteDict

import algLogic
import index
import path_utils
from paths import *

###########################
# Parameters and arguments
###########################

IPS = []

parser = argparse.ArgumentParser()
parser.add_argument("--predictive", default=False, action="store_true",
                    help="Predictively download sites based on semantic similarity. "
                         "Has high memory usage (1-2 GB).")
parser.add_argument("--debug", default=False, action="store_true",
                    help="Start Flask server in debug mode")
parser.add_argument("--port", default=8091,
                    help="Port on which to run server")
args = parser.parse_args()

###########################
# Globals
###########################

q = deque()

if args.predictive:
    doc2vec_model = gensim.models.Doc2Vec.load("doc2vec.bin")

search_index = index.Index()

download_blacklist = set()
with open(DOWNLOAD_BLACKLIST_PATH, "r") as blacklist_file:
    for site in blacklist_file:
        site = site.strip()
        download_blacklist.add(site)

app = Flask(__name__)


###########################
# Utility methods
###########################

def url_is_blacklisted(url):
    parse = urlsplit(url)
    domain = parse.netloc
    return domain in DOWNLOAD_BLACKLIST


def wget_command(url):
    """
    Return the parsed command for the wget command of a given url.
    """
    command = ['sleep 0.2;'
               'wget',
               '--header=\'Accept: text/html\'',
               '--user-agent=\'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0\'',
               '-e robots=off',
               '--dns-timeout=5',
               '--connect-timeout=5',
               '--tries=3',
               '--timestamping',
               '--convert-links',
               '--adjust-extension',
               '--page-requisites',
               '--span-hosts',
               '--directory-prefix={}'.format(WGET_DOWNLOADS),
               '-nv',
               '--span-hosts',
               '"' + url + '"',
               '2>&1 > /dev/null | ./worker.py']
    return ' '.join(command)


@app.before_first_request
def spawn_download_queue_watcher():
    def download_queue_watcher():
        subprocesses = []

        def download_next_url():
            # Get the next queued URL
            try:
                url = q.popleft()
                subprocesses.append(subprocess.Popen(wget_command(url), shell=True))
                # subprocesses[-1].wait()
            except IndexError:
                # The queue was empty, nothing to download
                return False

        while (True):
            for subproc in subprocesses:
                if subproc.poll() is not None:
                    subprocesses.remove(subproc)

            if len(q) and len(subprocesses) <= 4:
                download_next_url()

            time.sleep(0.1)

    thread = threading.Thread(target=download_queue_watcher)
    thread.start()


###########################
# Routes
###########################

@app.route("/visit", methods=['POST'])
def visit():
    # add to queue here and return fast
    url = request.form['url']
    access_time = request.form['access_time']
    query = request.form['query']

    print("[POST /visit] Visted {}".format(url))
    if not url_is_blacklisted(url):
        q.append(url)

   #if request.form['query']:
   #    results = google.search(request.form['query'], stop = 5)
   #    for result in results:
   #        q.append(result)
   #else:
   #    for link in algLogic.findAllLinks(url):
   #        if not url_is_blacklisted(link):
   #            q.append(link)

    if args.predictive:
        thread = threading.Thread(target=algLogic.main,
                                  args=[url, access_time,query, doc2vec_model, q])
        thread.start()

    return "Post Received! URL: {}\n".format(url)


if args.debug:
    @app.route("/check-q")
    def check_queue():
        """Debug method to see current items on the queue"""
        print(q)
        return "Printed queue contents", 200


@app.route("/search")
def search():
    # Get query_string from arguments
    query_string = request.args['query']
    print('[GET /search] Received query {}'.format(query_string))

    # Get search results from the index, and add in paths
    raw_results = search_index.search(query_string)

    # Copy results into dicts for modification and serialization
    results = [dict(result) for result in raw_results]

    for result in results:
        # TODO(ajayjain): Add in a synopsis of the article
        result['path'] = path_utils.strip_scheme(result['url'])
        result['body_text'] = result['summary_text']
        del result['summary_text']

    return jsonify(results)


@app.route("/retrieve/<path:url>", methods=['GET'])
def retrieve(url):
    with SqliteDict(RETRIEVE_CACHE_PATH) as url_map:
        url = path_utils.strip_scheme(url)
        try:
            path = url_map[url]
            if path.endswith('.html'):
                with open(os.path.join(WGET_DOWNLOADS, path), 'r') as f:
                    return f.read()
                    doc = Document(f.read())
                    print(doc.content())
                    return doc.content()
            else:
                return send_from_directory(WGET_DOWNLOADS, path)
        except KeyError:
            url_without_extension = url.rpartition('.')[0]
            try:
                path = url_map[url_without_extension]
                return send_from_directory(WGET_DOWNLOADS, path)
            except KeyError:
                return "not found!", 404


@app.route("/index_path")
def index_path():
    path = request.args['path']
    remote_url = "http://{}".format(path)
    path = os.path.join(WGET_DOWNLOADS, path)
    search_index.index_html(remote_url, path)
    return "Indexed {}".format(path)


def on_exit(signal, frame):
    """Clear queue to maintain queue thread safety"""
    print('You pressed Ctrl+C! Clearing dowload queue ({} items)...'
          .format(len(q)))
    while len(q) > 0:
        q.pop()
    print('Cleared queue.')
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, on_exit)
    app.run(port=args.port, debug=args.debug)

