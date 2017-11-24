import subprocess
import sys
from flask import Flask, request
app = Flask(__name__)

@app.route("/visit", methods=['POST'])
def visit():
    if request.method == 'POST':
        url = request.form['url']
        print(url)
        subprocess.Popen(wget_command(url), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return "Post Recieved!"

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
