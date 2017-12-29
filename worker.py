#!/usr/bin/env python

import logging
import os
from sqlitedict import SqliteDict
import sys

import index
from paths import *
import path_utils

# Initialize logger
os.makedirs(WGET_DIR, exist_ok=True)
with open(WORKER_LOG_PATH, 'a') as log_file:
    log_file.write('')
logger = logging.getLogger('worker')
hdlr = logging.FileHandler(WORKER_LOG_PATH)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

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


def is_html_file(path):
    return path.endswith('.html')


def process_wget_output(lines):
    ind = index.Index()

    logger.info('Worker processing lines')
    parsed_paths = []

    for line in lines:
        p = parse(line)

        logger.info('Worker input {}'.format(line))
        logger.info('Parsed {}'.format(p))

        if p is not None:
            parsed_paths.append(p)

    with SqliteDict(RETRIEVE_CACHE_PATH) as url_map:
        for remote_url, local_path in parsed_paths:
            local_path = local_path.replace(WGET_DOWNLOADS + "/", "")

            remote_url = path_utils.strip_scheme(remote_url)
            url_map[remote_url] = local_path

        url_map.commit()

    for remote_url, local_path in parsed_paths:
        if is_html_file(local_path):
            local_path = local_path.replace(WGET_DOWNLOADS + "/", "")
            logger.info('Found non-none path in wget output {} {}'.format(remote_url, local_path))
            ind.index_html(remote_url, local_path)

    logger.info('Worker EOF reached')

if __name__ == '__main__':
    process_wget_output(sys.stdin)

