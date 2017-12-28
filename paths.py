import os

CAULDRON_DIR = os.environ.get("CAULDRON_DIR", "")
WGET_DIR = os.path.join(CAULDRON_DIR, "wget")
WGET_DOWNLOADS = os.path.join(WGET_DIR, "downloads")

RETRIEVE_CACHE_PATH = os.path.join(CAULDRON_DIR, "url_map.db")
DOWNLOAD_BLACKLIST_PATH = os.path.join(CAULDRON_DIR, "download_blacklist.txt")

INDEX_DIR = os.path.join(CAULDRON_DIR, "index")

