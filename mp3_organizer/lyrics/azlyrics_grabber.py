__author__ = 'Ofir'

import re
from mp3_organizer.lyrics.lyrics_utils import encode, fetch_url, extract_text
from mp3_organizer.lyrics.base import Grabber

import logging
from mp3_organizer.organizer import LOGGER_NAME
logger = logging.getLogger(LOGGER_NAME)


class AZLyricsGrabber(Grabber):
    """
    Supplies simple functions for finding lyrics in 'AZ Lyrics'.
    """

    AZLYRICS_URL_PATTERN = 'http://www.azlyrics.com/lyrics/%s/%s.html'

    @staticmethod
    def get_name():
        return "AZ Lyrics"

    def find_lyrics(self, track, artist, album=None):
        """
        Searches 'az lyrics' for the lyrics.
        :param track: The track's title.
        :type track: str.
        :param artist: The artist's name.
        :type artist: str.
        :param album: The album's name.
        :type album: str.
        :returns: The track's lyrics, or None.
        """
        url = AZLyricsGrabber.AZLYRICS_URL_PATTERN % (self._encode(artist, is_artist=True),
                                                      self._encode(track))
        html = fetch_url(url, self.verbose)
        if not html:
            return

        lyrics = extract_text(html, "<!-- start of lyrics -->", self.verbose)
        if not lyrics and self.verbose:
            logger.debug("Couldn't find lyrics.")
        return lyrics

    def _encode(self, string, is_artist=False):
        """
        Encoding function specifically for 'AZ Lyrics'.
        :param string: The string to encode.
        :type string: str.
        :return: The encoded string.
        """
        string = re.sub('[^a-zA-Z0-9]', '', string).lower()
        if is_artist and string.startswith("the"):
            string = string[3:]
        return encode(string)

    def __repr__(self):
        """
        Prints the name of the website.
        """
        return "'AZ Lyrics' website"