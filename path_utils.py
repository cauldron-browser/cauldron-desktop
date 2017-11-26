from urllib.parse import urlparse

def is_html_document(remote_url, path):
    return (
        path.endswith('.html') and
        not remote_url.endswith('.js') and
        not remote_url.endswith('.css') and
        not remote_url.endswith('.jpg') and
        not remote_url.endswith('.png') and
        not remote_url.endswith('.bmp')
    )

# https://stackoverflow.com/a/21687728
def strip_scheme(url):
    parsed = urlparse(url)
    scheme = "%s://" % parsed.scheme
    return parsed.geturl().replace(scheme, '', 1)
