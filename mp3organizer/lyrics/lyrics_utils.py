import urllib
import re

import logbook

logger = logbook.Logger('LyricsUtils')

DIV_RE = re.compile(r'<(/?)div>?')
COMMENT_RE = re.compile(r'<!--.*-->', re.S)
TAG_RE = re.compile(r'<[^>]*>')
BREAK_RE = re.compile(r'<br\s*/?>')
URL_CHARACTERS = {
    '\u2018': '\'', '\u2019': '\'', '\u201c': '"',
    '\u201d': '"', '\u2010': '-', '\u2011': '-',
    '\u2012': '-', '\u2013': '-', '\u2014': '-',
    '\u2015': '-', '\u2016': '-', '\u2026': '...'
}


def extract_text(html, start_tag, verbose=True):
        """
        Extract the text from a <DIV> tag in the HTML starting with 'starttag'. Returns None if parsing fails.

        :param html: The HTML to extract the lyrics from.
        :param start_tag: The tag to start extraction after.
        :return: The extracted lyrics.
        """
        # Strip off the leading text before opening tag.
        try:
            _, html = html.split(start_tag, 1)
        except ValueError:
            if verbose:
                logger.debug('Couldn\'t find start tag - ' + start_tag + '.')
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
                logger.error('No closing tag found!')
            return
        lyrics = ''.join(parts)
        return strip_lyrics(lyrics)


def strip_lyrics(lyrics, whitespace_collapse=True):
    """
    Clean up HTML from an extracted lyrics string.
    For example, <BR> tags are replaced with newlines.

    :param lyrics: The lyrics to strip.
    :param whitespace_collapse: Whether or not to collapse whitespaces.
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
    :return: The encoded string.
    """
    for char, replace in URL_CHARACTERS.items():
        string = string.replace(char, replace)
    string = string.encode('UTF-8', errors='ignore')
    return urllib.parse.quote(string)


def unescape(text):
    """
    Resolves &#xxx; HTML entities (and some others).

    :param text: The text to unescape.
    :return: The unescaped text.
    """
    out = text.replace('&nbsp;', ' ')
    out = re.sub(r'&#(\d+);', lambda x: int(x.group(1)), out)
    return out


def fetch_url(url, verbose=True):
    """
    Retrieve the content at a given URL, or return None if the source is unreachable.

    :param url: The URL to fetch.
    :return: The content of this URL, or None.
    """
    try:
        return urllib.request.urlopen(url).read()
    except IOError:
        if verbose:
            logger.exception('failed to fetch: {}'.format(url))
        return None
