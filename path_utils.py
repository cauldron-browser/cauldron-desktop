from urllib.parse import urlparse

def strip_scheme(url):
    """Remove scheme from a URL
    
    Source: https://stackoverflow.com/a/21687728
    """
    parsed = urlparse(url)
    scheme = "%s://" % parsed.scheme
    return parsed.geturl().replace(scheme, '', 1)

