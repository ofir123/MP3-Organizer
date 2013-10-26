__author__ = 'Halti'

import urllib
import re

import logging
from mp3_organizer.organizer import LOGGER_NAME
logger = logging.getLogger(LOGGER_NAME)

DIV_RE = re.compile(r'<(/?)div>?')
COMMENT_RE = re.compile(r'<!--.*-->', re.S)
TAG_RE = re.compile(r'<[^>]*>')
BREAK_RE = re.compile(r'<br\s*/?>')
URL_CHARACTERS = {u'\u2018': u"'", u'\u2019': u"'", u'\u201c': u'"',
                  u'\u201d': u'"', u'\u2010': u'-', u'\u2011': u'-',
                  u'\u2012': u'-', u'\u2013': u'-', u'\u2014': u'-',
                  u'\u2015': u'-', u'\u2016': u'-', u'\u2026': u'...'}


def extract_text(html, start_tag, verbose=True):
        """
        Extract the text from a <DIV> tag in the HTML starting with
        'starttag'. Returns None if parsing fails.
        :param html: The HTML to extract the lyrics from.
        :type html: str.
        :param start_tag: The tag to start extraction after.
        :type start_tag: str.
        :return: The extracted lyrics.
        """
        # Strip off the leading text before opening tag.
        try:
            _, html = html.split(start_tag, 1)
        except ValueError:
            if verbose:
                logger.error("Couldn't find start tag - " + start_tag + ".")
            return

        # Walk through balanced DIV tags.
        level = 0
        parts = []
        pos = 0
        for match in DIV_RE.finditer(html):
            # Closing tag.
            if match.group(1):
                level -= 1
                if level == 0:
                    pos = match.end()
            # Opening tag.
            else:
                if level == 0:
                    parts.append(html[pos:match.start()])
                level += 1

            if level == -1:
                parts.append(html[pos:match.start()])
                break
        else:
            if verbose:
                logger.error("No closing tag found!")
            return
        lyrics = ''.join(parts)
        return strip_lyrics(lyrics)


def strip_lyrics(lyrics, whitespace_collapse=True):
    """
    Clean up HTML from an extracted lyrics string.
    For example, <BR> tags are replaced with newlines.
    :param lyrics: The lyrics to strip.
    :type lyrics: str.
    :param whitespace_collapse: Whether or not to collapse whitespaces.
    :type whitespace_collapse: bool.
    :return: The stripped lyrics.
    """
    lyrics = COMMENT_RE.sub('', lyrics)
    lyrics = unescape(lyrics)
    if whitespace_collapse:
        lyrics = re.sub(r'\s+', ' ', lyrics)
    # <BR> newlines.
    lyrics = BREAK_RE.sub('\n', lyrics)
    lyrics = re.sub(r'\n +', '\n', lyrics)
    lyrics = re.sub(r' +\n', '\n', lyrics)
    # Strip remaining HTML tags.
    lyrics = TAG_RE.sub('', lyrics)
    lyrics = lyrics.replace('\r', '\n')
    lyrics = lyrics.strip()
    return lyrics


def encode(string):
    """
    Encode the string for inclusion in a URL.
    :param string: The string to encode.
    :type string: str.
    :return: The encoded string.
    """
    if isinstance(string, unicode):
        for char, replace in URL_CHARACTERS.items():
            string = string.replace(char, replace)
        string = string.encode('utf8', 'ignore')
    return urllib.quote(string)


def unescape(text):
    """
    Resolves &#xxx; HTML entities (and some others).
    :param text: The text to unescape.
    :type text: str.
    :return: The unescaped text.
    """
    if isinstance(text, str):
        text = text.decode('utf8', 'ignore')
    out = text.replace(u'&nbsp;', u' ')
    out = re.sub(u"&#(\d+);", lambda x: unichr(int(x.group(1))), out)
    return out


def fetch_url(url, verbose=True):
    """
    Retrieve the content at a given URL, or return None if the source
    is unreachable.
    :param url: The URL to fetch.
    :type url: str.
    :return: The content of this URL, or None.
    """
    try:
        return urllib.urlopen(url).read()
    except IOError as ex:
        if verbose:
            logger.error("failed to fetch: " + url)
            print ex
        return None