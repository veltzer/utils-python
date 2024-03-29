"""
a module which knows how to download stuff from ted.com

References:
http://pranavashok.com/blog/2009/12/script-to-download-ted-videos-in-bulk/
"""

import urllib.request
import re
import download.generic


def get(link, file):
    ted_re = r"http://download.ted.com/talks/[\w_]+-480p.mp4"
    with urllib.request.urlopen(link) as web:
        web_content = web.read().decode()
    c = re.compile(ted_re)
    m = c.findall(web_content)
    if len(m) == 0:
        raise ValueError('no match')
    if len(m) != 1:
        raise ValueError('too many matches')
    url = m[0]
    download.generic.get(url, file)
