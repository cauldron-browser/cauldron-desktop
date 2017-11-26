from urllib.parse import urlparse

# https://stackoverflow.com/a/21687728
def strip_scheme(url):
    parsed = urlparse(url)
    scheme = "%s://" % parsed.scheme
    return parsed.geturl().replace(scheme, '', 1)
