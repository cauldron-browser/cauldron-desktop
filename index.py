import os

import whoosh.index
import whoosh.fields
import whoosh.qparser
import whoosh.writing

CAULDRON_DIR = os.environ.get("CAULDRON_DIR", "")
INDEX_DIR = os.path.join(CAULDRON_DIR, "index")

class Index(object):
    def __init__(self):
        # Initialize schema for index creation
        schema = whoosh.fields.Schema(title=whoosh.fields.TEXT(stored=True),
                                      url=whoosh.fields.ID(stored=True),
                                      body_text=whoosh.fields.TEXT)

        # Create index and index object. self.index can be shared between threads.
        if not os.path.exists(INDEX_DIR):
            print("Creating search index at {}".format(INDEX_DIR))
            os.mkdir(INDEX_DIR)
            self.index = whoosh.index.create_in(INDEX_DIR, schema)
        else:
            print("Loading search index at {}".format(INDEX_DIR))
            self.index = whoosh.index.open_dir(INDEX_DIR)

    def index_html(self, html_file_path):
        # Parse contents of HTML file
        # TODO(ajayjain): Deduplicate with Luis's code?

        # Add to the index
        index_parsed(title, url, body_text)

    def index_parsed(self, title, url, body_text):
        # TODO(ajayjain): Bulk write documents to the index
        writer = whoosh.writing.AsyncWriter(self.index)
        writer.add_document(title=title, url=url, body_text=body_text)
        writer.commit()

    def search(self, query_string):
        # Parse user query string
        query_parser = whoosh.qparser.QueryParser("body_text", self.index.schema)
        query = query_parser.parse(query_string)

        # Search for results in the index
        searcher = self.index.searcher()
        results = searcher.search(query)

        return results

