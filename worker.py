#!/usr/bin/env python

import os
import sys
import index

CAULDRON_DIR = os.environ.get("CAULDRON_DIR", "")
WGET_DIR = os.path.join(CAULDRON_DIR, "wget")
WGET_DOWNLOADS = os.path.join(WGET_DIR, "downloads")

def parse(line):
    """
    Return a tuple of (url, filepath) from a line of wget output. If
    it's not stuff we want to index, return None.
    """
    try:
        url_start = line.index(" URL:") + 5
        url_end = line.index(" [", url_start)
        url = line[url_start:url_end]
        filepath_start = line.index('-> "') + 4
        filepath_end = line.index('" ', filepath_start)
        filepath = line[filepath_start:filepath_end]
        return (url, filepath)
    except ValueError:
        return None

def main():
    ind = index.Index()
    for line in sys.stdin:
        p = parse(line)
        if p is not None:
            ind.index_html(*p)

if __name__ == '__main__':
    main()
