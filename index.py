import os

import whoosh.index
import whoosh.fields
import whoosh.qparser
import whoosh.writing

INDEX_DIR = os.environ.get("INDEX_DIR", "index")

schema = None
index = None
query_parser = None

def init():
    # Initialize schema and index
    schema = whoosh.fields.Schema(title=whoosh.fields.TEXT(stored=True),
                                  url=whoosh.fields.ID(stored=True),
                                  body_text=whoosh.fields.TEXT)

    if not os.path.exists(INDEX_DIR):
        print("Creating search index at {}".format(INDEX_DIR))
        os.mkdir(INDEX_DIR)
        index = whoosh.index.create_in(INDEX_DIR, schema)
    else:
        print("Loading search index at {}".format(INDEX_DIR))
        index = whoosh.index.open_dir(INDEX_DIR)

    # Create a query_parser that searches the body text by default
    query_parser = whoosh.qparser.QueryParser("body_text", index.schema)

def index_html(html_file_path):
    # Parse contents of HTML file
    # TODO(ajayjain): Deduplicate with Luis's code?

    # Add to the index
    index_parsed(title, url, body_text)

def index_parsed(title, url, body_text):
    # TODO(ajayjain): Bulk write documents to the index
    writer = whoosh.writing.AsyncWriter(index)
    writer.add_document(title=title, url=url, body_text=body_text)
    writer.commit()

def search(query_string):
    query = query_parser.parse(query_string)
    searcher = index.searcher()
    results = searcher.search(query)
    return results

init()
