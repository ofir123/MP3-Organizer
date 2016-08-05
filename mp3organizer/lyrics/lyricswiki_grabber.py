import re

import logbook

from .lyrics_utils import encode, fetch_url, extract_text
from .base import Grabber

logger = logbook.Logger('LyricsWikiGrabber')


class LyricswikiGrabber(Grabber):
    """
    Supplies simple functions for finding lyrics in "Lyrics Wiki".
    """

    LYRICSWIKI_URL_PATTERN = 'http://lyrics.wikia.com/{}:{}'

    @staticmethod
    def get_name():
        return 'Lyrics Wiki'

    def find_lyrics(self, track, artist, album=None):
        """
        Searches "Lyrics Wiki" for the lyrics.

        :param track: The track's title.
        :param artist: The artist's name.
        :param album: The album's name.
        :returns: The track's lyrics, or None.
        """
        url = LyricswikiGrabber.LYRICSWIKI_URL_PATTERN.format(self._encode(artist), self._encode(track))
        html = fetch_url(url, self.verbose)
        if not html:
            return

        lyrics = extract_text(html, '<div class="lyricbox">', self.verbose)
        if lyrics and 'Unfortunately, we are not licensed' not in lyrics:
            return lyrics
        if self.verbose:
            logger.debug('Couldn\'t find lyrics.')

    @staticmethod
    def _encode(string):
        """
        Encoding function specifically for 'Lyrics Wiki'.

        :param string: The string to encode.
        :return: The encoded string.
        """
        string = re.sub(r'\s+', '_', string)
        string = string.replace('<', 'Less_Than')
        string = string.replace('>', 'Greater_Than')
        string = string.replace('#', 'Number_')
        string = re.sub(r'[\[\{]', '(', string)
        string = re.sub(r'[\]\}]', ')', string)
        return encode(string)

    def __repr__(self):
        """
        Prints the name of the website.
        """
        return '"Lyrics Wiki" website'
