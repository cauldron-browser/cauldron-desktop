import subprocess
import sys
import time
import threading
from multiprocessing import Queue
from urllib.parse import urlsplit
from collections import deque
from flask import Flask, request, jsonify, send_from_directory

import index
import os

global q
q = deque()

CAULDRON_DIR = os.environ.get("CAULDRON_DIR", "")
WGET_DIR = os.path.join(CAULDRON_DIR, "wget")
WGET_DOWNLOADS = os.path.join(WGET_DIR, "downloads")

def wget_command(url):
    """
    Return the parsed command for the wget command of a given url.
    """
    command = ['wget',
               '--header=\'Accept: text/html\'',
               '--user-agent=\'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0\'',
               '--recursive',
               '--timestamping',
               '--no-remove-listing',
               '--convert-links',
               '--adjust-extension',
               '--page-requisites',
               '--no-parent',
               '--directory-prefix={}'.format(WGET_DOWNLOADS),
               '-nv',
               url,
               '2>&1 > /dev/null | ./worker.py']
    return ' '.join(command)

def create_app():
    app = Flask(__name__)
    app.config['index'] = index.Index()
    return app


app = create_app()

@app.before_first_request
def activate_job():
    def stupid():
        listOfSubs = []
        def multiThreadedwget(url):
            while (len(listOfSubs) > 4):
                time.sleep(0.15)
            #remove any process that finished
            for sb in listOfSubs:
                if sb.poll() is not None:
                    listOfSubs.remove(sb)
            #listOfSubs.append(subprocess.Popen(wget_command(url), stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            listOfSubs.append(subprocess.Popen(wget_command(url), shell=True))

        while (True):
            # print(q)
            for sb in listOfSubs:
                if sb.poll() is not None:
                    listOfSubs.remove(sb)
            if (len(q)>0):
                wget_job = q.popleft()
                print('Got wget_job: ', wget_job)
                multiThreadedwget(wget_job)
            time.sleep(0.06)
    thread = threading.Thread(target=stupid)
    thread.start()


@app.route("/visit", methods=['POST'])
def visit():
    #add to queue here and return fast
    url = request.form['url']
    print("[POST /visit] Visted {}".format(url))
    q.append(url)
    for link in algLogic.findAllLinks(url):
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

    for result in results:
        # TODO(ajayjain): Add in a synopsis of the article
        result['path'] = get_path(result['url'])

    return jsonify(results)

@app.route("/retrieve/<path:path>", methods=['GET'])
def retrieve(path):
    parsed = urlsplit(path)
    return send_from_directory('wget/downloads', parsed.netloc + parsed.path + "index.html")

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

