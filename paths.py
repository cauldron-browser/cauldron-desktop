import os

CAULDRON_DIR = os.environ.get("CAULDRON_DIR", "")
WGET_DIR = os.path.join(CAULDRON_DIR, "wget")
WGET_DOWNLOADS = os.path.join(WGET_DIR, "downloads")

RETRIEVE_CACHE_PATH = os.path.join(CAULDRON_DIR, "url_map.db")

INDEX_DIR = os.path.join(CAULDRON_DIR, "index")

WORKER_LOG_PATH = os.path.join(WGET_DIR, 'worker.log')

# SOURCE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DOWNLOAD_BLACKLIST_PATH = os.path.join(CAULDRON_DIR, "download_blacklist.txt")

