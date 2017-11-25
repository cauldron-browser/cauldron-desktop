import subprocess
import sys
import time
import threading
from multiprocessing import Queue

from collections import deque
from flask import Flask, request, jsonify

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
    #return the -r here JASON SEIBEL
    return 'wget --header="Accept: text/html" --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0"  -r -N --no-remove-listing --convert-links --adjust-extension --page-requisites --no-parent --directory-prefix={} {}'.format(WGET_DOWNLOADS, url).split()

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
            # print(listOfSubs)
            # print("subprocess started")
            listOfSubs.append(subprocess.Popen(wget_command(url), stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
            # print(listOfSubs[0].poll())

        while (True):
            # print("the thread is running")
            # print("length of queue is: " + str(len(q)))
            # print("current subprocces count is:" + str(len(listOfSubs)))
            # print(listOfSubs)
            for sb in listOfSubs:
                # print(sb.poll())
                if sb.poll() is not None:
                    listOfSubs.remove(sb)
            if (len(q)>0):
                # print("pop attempt")
                multiThreadedwget(q.popleft())
            time.sleep(0.06)
    thread = threading.Thread(target=stupid)
    thread.start()      


@app.route("/visit", methods=['POST'])
def visit():
    # print("POST")
    if request.method == 'POST':
        #add to queue here and return fast
        url = request.form['url']
        print(url)
        q.append(url)
        # print(q)
        return "Post Received!"

@app.route("/search")
def search():
    # Get query_string from arguments
    query_string = request.args['query']
    print('[GET /search] Received query {}'.format(query_string))

    # Get search results from the index, and add in paths
    results = app.config['index'].search(query_string)
    for result in results:
        # TODO(ajayjain): Add in a synopsis of the article
        # result['path'] = path_from_url(result['url'])
        result['path'] = result['url']

    # to make results serializable
    results = [dict(r) for r in results]

    return jsonify(results)

@app.route("/retrieve/<path:path>")
def retrieve(path):
    return app.send_static_file(os.path.join('name_of_folder_that_holds_cache', path).replace('\\','/'))

@app.route("/index_path")
def index_path():
    path = request.args['path']
    remote_url = "http://{}".format(path)
    path = os.path.join("downloads", path)
    app.config['index'].index_html(remote_url, path)
    return "Indexed {}".format(path)

if __name__ == '__main__':
    app.run(port=8091)
