import os
import subprocess
import sys
import time
import threading
from multiprocessing import Queue
from urllib.parse import urlsplit
from collections import deque
import google
import path_utils

from flask import Flask, request, jsonify, send_from_directory, redirect, render_template

import algLogic
import index
from sqlitedict import SqliteDict

global q
q = deque()

CAULDRON_DIR = os.path.dirname(os.path.realpath(__file__))
# CAULDRON_DIR = os.environ.get("CAULDRON_DIR", "")
WGET_DIR = "wget"
WGET_DOWNLOADS = os.path.join(WGET_DIR, "downloads")
RETRIEVE_CACHE_PATH = os.path.join(CAULDRON_DIR, "url_map.db")

DOWNLOAD_BLACKLIST = ['www.google.com', 'www.google.fi']

def url_is_blacklisted(url):
    parse = urlsplit(url)
    domain = parse.netloc 
    return domain in DOWNLOAD_BLACKLIST

def wget_command(url):
    """
    Return the parsed command for the wget command of a given url.
    """
    command = ['wget',
               '--header=\'Accept: text/html\'',
               '--user-agent=\'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0\'',
               '-e robots=off',
               '--timestamping',
               '--convert-links',
               '--adjust-extension',
               '--page-requisites',
               '--span-hosts',
               '--directory-prefix={}'.format(WGET_DOWNLOADS),
               '-nv',
               '"' + url + '"',
               '2>&1 > /dev/null | ./worker.py']
    return ' '.join(command)

def create_app():
    app = Flask(__name__)
    app.config['index'] = index.Index()
    return app

# wget --header="Accept: text/html" --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0" -e robots=off --timestamping --convert-links --adjust-extension --page-requisites --span-hosts

app = create_app()


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


@app.route("/visit", methods=['POST'])
def visit():
    #add to queue here and return fast
    url = request.form['url']
    print("[POST /visit] Visted {}".format(url))
    if not url_is_blacklisted(url):
        q.append(url)
    if request.form['query']:
        results = google.search(request.form['query'], stop = 5)
        for result in results:
            q.append(result)
    else:
        for link in algLogic.findAllLinks(url):
            if not url_is_blacklisted(link):
                q.append(link)
    return "Post Received! URL: {}\n".format(url)

def get_path(url):
    return url.replace("http://", "").replace("https://", "")

@app.route("/search")
def search():
    # Get query_string from arguments
    query_string = request.args['query']
    print('[GET /search] Received query {}'.format(query_string))

    # Get search results from the index, and add in paths
    raw_results = app.config['index'].search(query_string)

    # Copy results into dicts for modification and serialization
    results = [dict(result) for result in raw_results]

    # Add the local filesystem path to each search result
    with SqliteDict(RETRIEVE_CACHE_PATH) as url_map:
        for result in results:
            # TODO(ajayjain): Add in a synopsis of the article
            url = path_utils.strip_scheme(result['url'])
            try:
                result['path'] = "file://" + os.path.join(CAULDRON_DIR, WGET_DOWNLOADS, url_map[url])
            except KeyError as e:
                print("[GET /search] Error looking up URL in map", url, e)

    return jsonify(results)

@app.route("/retrieve/<path:url>", methods=['GET'])
def retrieve(url):
    with SqliteDict(RETRIEVE_CACHE_PATH) as url_map:
        try:
            url = path_utils.strip_scheme(url)
            path = url_map[url]
            #redirect_url = "file://" + os.path.join(CAULDRON_DIR, WGET_DOWNLOADS, path)
            #print("[GET /retrieve/<path:url>] Redirecting to", redirect_url)
            return send_from_directory(WGET_DOWNLOADS, path)
        except KeyError:
            return "not found!", 404

@app.route("/index_path")
def index_path():
    path = request.args['path']
    remote_url = "http://{}".format(path)
    path = os.path.join(WGET_DOWNLOADS, path)
    app.config['index'].index_html(remote_url, path)
    return "Indexed {}".format(path)

if __name__ == '__main__':
    import signal
    def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        # clear queue 
        # maintains queue thread safety
        while len(q) > 0:
            q.pop()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    app.run(port=8091, debug=True)
