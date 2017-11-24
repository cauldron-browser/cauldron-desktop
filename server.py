from flask import Flask
app = Flask(__name__)

@app.route("visit")
def visit():
    return "Hello World!"

@app.route("search")
def search():
    return "Hello World!"

@app.route("/retrieve/<path:path>")
def retrieve():
    return return app.send_static_file(os.path.join('name_of_folder_that_holds_cache', path).replace('\\','/'))