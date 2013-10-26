__author__ = 'Ofir'

import re
from lyrics_utils import encode, fetch_url, extract_text
from mp3_organizer.lyrics.base import Grabber

import logging
from mp3_organizer.organizer import LOGGER_NAME
logger = logging.getLogger(LOGGER_NAME)


class LyricscomGrabber(Grabber):
    """
    Supplies simple functions for finding lyrics in 'lyrics.com'.
    """

    LYRICSCOM_URL_PATTERN = 'http://www.lyrics.com/%s-lyrics-%s.html'
    LYRICSCOM_NOT_FOUND = ('Sorry, we do not have the lyric', 'Submit Lyrics')

    @staticmethod
    def get_name():
        return "Lyrics.com"

    def find_lyrics(self, track, artist, album=None, prompt=True, web=True):
        """
        Searches 'lyrics.com' for the lyrics.
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
        url = LyricscomGrabber.LYRICSCOM_URL_PATTERN % (self._encode(track),
                                                        self._encode(artist))
        html = fetch_url(url, self.verbose)
        if not html:
            return

        lyrics = extract_text(html, '<div id="lyric_space">', self.verbose)
        if not lyrics:
            return
        for not_found_str in LyricscomGrabber.LYRICSCOM_NOT_FOUND:
            if not_found_str in lyrics:
                if self.verbose:
                    logger.warning("Couldn't find lyrics.")
                return

        parts = lyrics.split('\n---\nLyrics powered by', 1)
        if parts:
            return parts[0]
        if self.verbose:
            logger.error("Something went wrong when splitting the parts.")

    def _encode(self, string):
        """
        Encoding function specifically for 'Lyrics.com'.
        :param string: The string to encode.
        :type string: str.
        :return: The encoded string.
        """
        string = re.sub(r'[^\w\s-]', '', string)
        string = re.sub(r'\s+', '-', string)
        return encode(string).lower()

    def __repr__(self):
        """
        Prints the name of the website.
        """
        return "'Lyrics.com' website"