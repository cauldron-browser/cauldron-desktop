from collections import namedtuple
import os
import sys

from bs4 import BeautifulSoup
import lxml
import readability
import whoosh.index
import whoosh.fields
import whoosh.qparser
import whoosh.writing

from paths import *
import path_utils


ParsedDocument = namedtuple("ParsedDocument", ["title", "content"])


def parse_html_string(html_string):
    # Parse out title and body text
    document = readability.Document(html_string)

    # TODO(ajayjain): use document.short_title()?
    title = document.title()
    body_html = document.summary(html_partial=True)
    body_text = BeautifulSoup(body_html, 'lxml').get_text().strip()
    parsed = ParsedDocument(title=title, content=body_text)

    return parsed


def make_preview(text, max_length=250):
    """Return an excerpt view of a string"""
    preview = text.replace("\n", " ").strip()

    if len(preview) > max_length:
        preview = preview[:max_length-3].strip() + "..."

    return preview


class Index(object):
    def __init__(self):
        # Initialize schema for index creation
        schema = whoosh.fields.Schema(title=whoosh.fields.TEXT(stored=True),
                                      url=whoosh.fields.ID(stored=True, unique=True),
                                      body_text=whoosh.fields.TEXT(stored=True))

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

        try:
            parsed = parse_html_string(content)
            # Add to the index
            self.index_parsed(parsed.title, remote_url, parsed.content)
        except lxml.etree.ParserError as err:
            print("ParserError while parsing HTML content:", err)
            print("\tremote url:", remote_url)
            print("\tlocal path:", local_path)

    def index_parsed(self, title, url, body_text):
        preview = make_preview(body_text, max_length=100)

        print("[index index_parsed] Indexing...")
        print("\turl:  ", url)
        print("\ttitle:", title)
        print("\tbody: ", preview)

        if body_text:
            # TODO(ajayjain): Bulk write documents to the index
            # Wrapping the AsyncWriter in a with clause seems to cause errors:
            #     "whoosh.writing.IndexingError: This writer is closed"
            writer = whoosh.writing.AsyncWriter(self.index)
            writer.update_document(
                    title=title,
                    url=url,
                    body_text=body_text)
            writer.commit()
        else:
            print("No content extracted, not indexing\n")

    def search(self, query_string):
        """Search for results in the index by a query string"""
        # Parse user query string
        query_parser = whoosh.qparser.QueryParser("body_text", self.index.schema)
        query = query_parser.parse(query_string)

        searcher = self.index.searcher()
        raw_results = searcher.search(query, terms=True)

        results = []
        for hit in raw_results:
            result = {}
            result['title'] = hit['title']
            result['url'] = hit['url']
            # Remove scheme from URL displayed to user
            result['path'] = path_utils.strip_scheme(hit['url'])
            # Display highlighted text at keywords
            result['body_text'] = hit.highlights("body_text")
            results.append(result)

        return results

