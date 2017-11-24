import subprocess
import sys
import time
from flask import Flask, request
global listOfSubs
listOfSubs = []
app = Flask(__name__)

@app.route("/visit", methods=['POST'])
def visit():
    
    if request.method == 'POST':
        url = request.form['url']
        print(url)
        #OnExit is callback to limit number of subprocesses to 2
        while (len(listOfSubs) > 3):
            time.sleep(0.3)
            #remove any process that finished
            for sb in listOfSubs:
                if sb.poll() is 0:
                    listOfSubs.remove(sb)
        listOfSubs.append(subprocess.Popen(wget_command(url), stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        return "Post Received!"


@app.route("/search")
def search():
    return "Hello World!"

@app.route("/retrieve/<path:path>")
def retrieve():
    return app.send_static_file(os.path.join('name_of_folder_that_holds_cache', path).replace('\\','/'))

def wget_command(url):
    """
    Return the parsed command for the wget command of a given url.
    """
    return "wget -r -N --no-remove-listing --convert-links --adjust-extension --page-requisites --no-parent {}".format(url).split()

if __name__ == '__main__':
    app.run(threaded=True)
