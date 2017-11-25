import os

import whoosh.index
import whoosh.fields
import whoosh.qparser
import whoosh.writing

INDEX_DIR = os.environ.get("INDEX_DIR", "index")

class Index(object):
    def __init__(self):
        # Initialize schema and index
        schema = whoosh.fields.Schema(title=whoosh.fields.TEXT(stored=True), 
                                      url=whoosh.fields.ID(stored=True), 
                                      body_text=whoosh.fields.TEXT)

        if not os.path.exists(INDEX_DIR):
            print("Creating search index at {}".format(INDEX_DIR))
            os.mkdir(INDEX_DIR)
            self.index = whoosh.index.create_in(INDEX_DIR, schema)
        else:
            print("Loading search index at {}".format(INDEX_DIR))
            self.index = whoosh.index.open_dir(INDEX_DIR)

        # Create a query_parser that searches the body text by default
        self.query_parser = whoosh.qparser.QueryParser("body_text", self.index.schema)

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
        query = self.query_parser.parse(query_string)
        searcher = self.index.searcher()
        results = searcher.search(query)
        return results

