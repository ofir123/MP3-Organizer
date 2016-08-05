import re

import logbook

from .lyrics_utils import encode, fetch_url, extract_text
from .base import Grabber

logger = logbook.Logger('LyricsComGrabber')


class LyricscomGrabber(Grabber):
    """
    Supplies simple functions for finding lyrics in "lyrics.com".
    """

    LYRICSCOM_URL_PATTERN = 'http://www.lyrics.com/{}-lyrics-{}.html'
    LYRICSCOM_NOT_FOUND = ('Sorry, we do not have the lyric', 'Submit Lyrics')

    @staticmethod
    def get_name():
        return 'Lyrics.com'

    def find_lyrics(self, track, artist, album=None):
        """
        Searches "lyrics.com" for the lyrics.

        :param track: The track's title.
        :param artist: The artist's name.
        :param album: The album's name.
        :returns: The track's lyrics, or None.
        """
        url = LyricscomGrabber.LYRICSCOM_URL_PATTERN.format(self._encode(track), self._encode(artist))
        html = fetch_url(url, self.verbose)
        if not html:
            return

        lyrics = extract_text(html, '<div id="lyric_space">', self.verbose)
        if not lyrics and self.verbose:
            logger.debug('Couldn\'t find lyrics.')
            return
        for not_found_str in LyricscomGrabber.LYRICSCOM_NOT_FOUND:
            if not_found_str in lyrics:
                if self.verbose:
                    logger.debug('Couldn\'t find lyrics.')
                return

        parts = lyrics.split('\n---\nLyrics powered by', 1)
        if parts:
            return parts[0]
        if self.verbose:
            logger.error('Something went wrong when splitting the parts.')

    @staticmethod
    def _encode(string):
        """
        Encoding function specifically for 'Lyrics.com'.

        :param string: The string to encode.
        :return: The encoded string.
        """
        string = re.sub(r'[^\w\s-]', '', string)
        string = re.sub(r'\s+', '-', string)
        return encode(string).lower()

    def __repr__(self):
        """
        Prints the name of the website.
        """
        return '"Lyrics.com" website'
