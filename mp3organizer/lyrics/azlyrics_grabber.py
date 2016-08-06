import re

import logbook

from .lyrics_utils import encode, fetch_url, extract_text
from .base import Grabber

logger = logbook.Logger('AZLyricsGrabber')


class AZLyricsGrabber(Grabber):
    """
    Supplies simple functions for finding lyrics in "AZ Lyrics".
    """

    AZLYRICS_URL_PATTERN = 'http://www.azlyrics.com/lyrics/{}/{}.html'

    @staticmethod
    def get_name():
        return 'AZ Lyrics'

    def find_lyrics(self, track, artist, album=None):
        """
        Searches "AZ Lyrics" for the lyrics.

        :param track: The track's title.
        :param artist: The artist's name.
        :param album: The album's name.
        :returns: The track's lyrics, or None.
        """
        url = AZLyricsGrabber.AZLYRICS_URL_PATTERN.format(self._encode(artist, is_artist=True), self._encode(track))
        html = fetch_url(url, self.verbose)
        if not html:
            return

        lyrics = extract_text(html, '<!-- Usage of azlyrics.com content by any third-party lyrics provider is '
                                    'prohibited by our licensing agreement. Sorry about that. -->', self.verbose)
        if not lyrics and self.verbose:
            logger.debug('Couldn\'t find lyrics.')
        return lyrics

    @staticmethod
    def _encode(string, is_artist=False):
        """
        Encoding function specifically for 'AZ Lyrics'.

        :param string: The string to encode.
        :param is_artist: If True, "The" will be omitted.
        :return: The encoded string.
        """
        string = re.sub('[^a-zA-Z0-9]', '', string).lower()
        if is_artist and string.startswith('the'):
            string = string[3:]
        return encode(string)

    def __repr__(self):
        """
        Prints the name of the website.
        """
        return '"AZ Lyrics" website'
