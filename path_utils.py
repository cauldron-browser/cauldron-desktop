import html
from urllib import parse

def strip_scheme(url):
    """Remove scheme from a URL

    Source: https://stackoverflow.com/a/21687728
    """
    parsed = parse.urlparse(url)
    scheme = "%s://" % parsed.scheme
    return parsed.geturl().replace(scheme, '', 1)


def strip_extension(url):
    return url.rpartition('.')[0]


def unescape(url):
    url_unencoded = parse.unquote_plus(url)
    html_unescaped = html.unescape(url_unencoded)
    return html_unescaped

