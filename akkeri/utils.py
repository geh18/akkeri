# encoding=utf8

import translitcodec
import re
import HTMLParser


def slugify(s, fallback=u'no-slug'):
    """
    Generates an ASCII-only slug from the input string.
    If the generation fails (i.e. if the input has no word characters),
    it returns the `fallback` string, which by default is 'no-slug'.
    """
    if isinstance(s, str):
        s = s.decode('utf-8')
    s = unescape_entities(s)
    cleaned = s.encode('translit/long').lower()
    words = [_ for _ in re.split(r'\W+', cleaned) if _]
    return unicode('-'.join(words)) or fallback


def unescape_entities(html):
    "Converts HTML entities (both named and numeric) to Unicode."
    if not html:
        return ''
    h = HTMLParser.HTMLParser()
    return h.unescape(html)
