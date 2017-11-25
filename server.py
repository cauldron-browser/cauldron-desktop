import subprocess
import sys
import time
from flask import Flask, request
import threading
from multiprocessing import Queue
from collections import deque

global q
q = deque()

def wget_command(url):
    """
    Return the parsed command for the wget command of a given url.
    """
    #change this to desired wget function
    return "wget --mirror --convert-links --adjust-extension --page-requisites --no-parent {}".format(url).split()


def create_app():
    app = Flask(__name__)
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
    # thread.join() 

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
    return "Hello World!"

@app.route("/retrieve/<path:path>")
def retrieve():
    return app.send_static_file(os.path.join('name_of_folder_that_holds_cache', path).replace('\\','/'))

if __name__ == '__main__':
    app.run(port=8091)
