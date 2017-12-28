from collections import namedtuple
import os
import sys

from bs4 import BeautifulSoup
import readability
import whoosh.index
import whoosh.fields
import whoosh.qparser
import whoosh.writing

from paths import *


ParsedDocument = namedtuple("ParsedDocument", ["title", "content"])


def parse_html_string(html_string):
    # Parse out title and summary
    document = readability.Document(html_string)

    # TODO(ajayjain): use document.short_title()?
    title = document.title()
    body_html = document.summary(html_partial=True)
    body_text = BeautifulSoup(body_html, 'lxml').get_text().strip()
    parsed = ParsedDocument(title=title, content=body_text)

    return parsed


class Index(object):
    def __init__(self):
        # Initialize schema for index creation
        schema = whoosh.fields.Schema(title=whoosh.fields.TEXT(stored=True),
                                      url=whoosh.fields.ID(stored=True, unique=True),
                                      body_text=whoosh.fields.TEXT(stored=False),
                                      summary_text=whoosh.fields.TEXT(stored=True))

        # Create index and index object. self.index can be shared between threads.
        if not os.path.exists(INDEX_DIR):
            print("Creating search index at {}".format(INDEX_DIR))
            os.mkdir(INDEX_DIR)
            self.index = whoosh.index.create_in(INDEX_DIR, schema)
        else:
            print("Loading search index at {}".format(INDEX_DIR))
            self.index = whoosh.index.open_dir(INDEX_DIR)

    def index_html(self, remote_url, local_path):
        # TODO(ajayjain): Switch to boilerpipe / a python wrapper
        # TODO(ajayjain): Deduplicate with Luis's code

        # Load HTML file
        content = ""
        with open(os.path.join(WGET_DOWNLOADS, local_path), 'r') as html_file:
            try:
                content = html_file.read()
            except UnicodeDecodeError as e:
                print('UnicodeDecodeError in Index, reading a file', e)
                return

        parsed = parse_html_string(content)

        # Add to the index
        self.index_parsed(parsed.title, remote_url, parsed.content)

    def index_parsed(self, title, url, body_text):
        print("[index index_parsed] Indexing...")
        print("\t\t url:", url)
        print("\t\t title:", title)
        print("\t\t body:", body_text[:250], "...")
        summary = ' '.join(body_text.split())[:250] + "..."

        # TODO(ajayjain): Bulk write documents to the index
        # Wrapping the AsyncWriter in a with clause seems to cause errors:
        #     "whoosh.writing.IndexingError: This writer is closed"
        writer = whoosh.writing.AsyncWriter(self.index)
        writer.update_document(title=title, url=url, body_text=body_text, summary_text=summary)
        writer.commit()

    def search(self, query_string):
        """Search for results in the index by a query string"""
        # Parse user query string
        query_parser = whoosh.qparser.QueryParser("body_text", self.index.schema)
        query = query_parser.parse(query_string)

        searcher = self.index.searcher()
        return searcher.search(query)

