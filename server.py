import subprocess
import sys
import time
import threading
from multiprocessing import Queue

from flask import Flask, request, jsonify

import index
import os

global q
q = Queue(maxsize=0)
global listOfSubs
listOfSubs = []



class queueDownloader (threading.Thread):
    def __init__(self, threadID, name):
       threading.Thread.__init__(self)
       self.threadID = threadID
       self.name = name
    def run(self):
        
        #run this function whenever stuff is in queue
        

        def multiThreadedwget(url):
            print(listOfSubs)
            while (len(listOfSubs) > 3):
                time.sleep(0.15)
            #remove any process that finished
            for sb in listOfSubs:
                if sb.poll() is 0:
                    listOfSubs.remove(sb)
            print(listOfSubs)
            listOfSubs.append(subprocess.Popen(wget_command(url), stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        while (True):
            if (True): #q.qsize()>0 here 
                multiThreadedwget(q.get())
            time.sleep(0.15)
            print(listOfSubs)

def create_app():
   thread1 = queueDownloader(1, "Thread-1")
   thread1.start()
   
   app = Flask(__name__)
   app.config['index'] = index.Index()
   return app
app = create_app()

@app.route("/visit", methods=['POST'])
def visit():
    
    if request.method == 'POST':
        #add to queue here and return fast
        url = request.form['url']
        print(url)
        q.put(url)
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

def wget_command(url):
    """
    Return the parsed command for the wget command of a given url.
    """
    #return the -r here JASON SEIBEL
    return
        """wget \
            -N \
            --no-remove-listing \
            --convert-links \
            --adjust-extension \
            --page-requisites \
            --no-parent \
            --user-agent "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36" \
            {}".format(url).split()"""

if __name__ == '__main__':
    app.run(threaded=True)