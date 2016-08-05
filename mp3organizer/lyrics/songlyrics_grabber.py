import re

import logbook

from .lyrics_utils import encode, fetch_url, extract_text
from .base import Grabber

logger = logbook.Logger('SongLyricsGrabber')


class SongLyricsGrabber(Grabber):
    """
    Supplies simple functions for finding lyrics in "Song Lyrics".
    """

    SONGLYRICS_URL_PATTERN = 'http://www.songlyrics.com/{}/{}-lyrics/'
    SONGLYRICS_NOT_FOUND = ('We do not have the lyrics', 'Sorry, we have no')

    @staticmethod
    def get_name():
        return 'Song Lyrics'

    def find_lyrics(self, track, artist, album=None):
        """
        Searches "Song Lyrics" for the lyrics.

        :param track: The track's title.
        :param artist: The artist's name.
        :param album: The album's name.
        :returns: The track's lyrics, or None.
        """
        url = SongLyricsGrabber.SONGLYRICS_URL_PATTERN.format(self._encode(artist), self._encode(track))
        html = fetch_url(url, self.verbose)
        if not html:
            return

        lyrics = extract_text(html, '<div id="songLyricsDiv-outer">', self.verbose)
        if not lyrics and self.verbose:
            logger.debug('Couldn\'t find lyrics.')
            return
        for not_found_str in SongLyricsGrabber.SONGLYRICS_NOT_FOUND:
            if not_found_str in lyrics:
                if self.verbose:
                    logger.debug('Couldn\'t find lyrics.')
                return
        return lyrics

    @staticmethod
    def _encode(string):
        """
        Encoding function specifically for "Song Lyrics".

        :param string: The string to encode.
        :return: The encoded string.
        """
        string = re.sub('[^a-zA-Z0-9]', '-', string).lower()
        if string.endswith('-'):
            string = string[:-1]
        return encode(string)

    def __repr__(self):
        """
        Prints the name of the website.
        """
        return '"Song Lyrics" website'
