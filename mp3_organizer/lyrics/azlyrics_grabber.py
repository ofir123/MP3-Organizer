__author__ = 'Ofir'

import re
from lyrics_utils import encode, fetch_url, extract_text
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

    def find_lyrics(self, track, artist, album=None, prompt=True, web=True):
        """
        Searches 'lyrics wiki' for the lyrics.
        :param track: The track's title.
        :type track: str.
        :param artist: The artist's name.
        :type artist: str.
        :param album: The album's name.
        :type album: str.
        :param prompt: Whether or not to prompt the user for approval.
        :type prompt: bool.
        :param web: Whether or not to open a browser with the album's information.
        :type web: bool.
        :returns: The track's lyrics, or None.
        """
        url = AZLyricsGrabber.AZLYRICS_URL_PATTERN % (self._encode(artist),
                                                      self._encode(track))
        html = fetch_url(url, self.verbose)
        if not html:
            return

        lyrics = extract_text(html, "<!-- start of lyrics -->", self.verbose)
        if not lyrics and self.verbose:
            logger.debug("Couldn't find lyrics.")
        return lyrics

    def _encode(self, string):
        """
        Encoding function specifically for 'AZ Lyrics'.
        :param string: The string to encode.
        :type string: str.
        :return: The encoded string.
        """
        string = re.sub('[^a-zA-Z0-9]', '', string)
        return encode(string.lower())

    def __repr__(self):
        """
        Prints the name of the website.
        """
        return "'AZ Lyrics' website"