__author__ = 'Ofir'

import re
from lyrics_utils import encode, fetch_url, extract_text
from mp3_organizer.lyrics.base import Grabber


class LyricswikiGrabber(Grabber):
    """
    Supplies simple functions for finding lyrics in 'lyrics wiki'.
    """

    LYRICSWIKI_URL_PATTERN = 'http://lyrics.wikia.com/%s:%s'

    @property
    def name(self):
        return "Lyrics Wiki"

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
        url = LyricswikiGrabber.LYRICSWIKI_URL_PATTERN % (self._encode(artist),
                                                          self._encode(track))
        html = fetch_url(url, self.verbose)
        if not html:
            return

        lyrics = extract_text(html, "<div class='lyricbox'>", self.verbose)
        if lyrics and 'Unfortunately, we are not licensed' not in lyrics:
            return lyrics
        if self.verbose:
            print "Couldn't find lyrics."

    def _encode(self, string):
        """
        Encoding function specifically for 'Lyrics Wiki'.
        :param string: The string to encode.
        :type string: str.
        :return: The encoded string.
        """
        string = re.sub(r'\s+', '_', string)
        string = string.replace("<", "Less_Than")
        string = string.replace(">", "Greater_Than")
        string = string.replace("#", "Number_")
        string = re.sub(r'[\[\{]', '(', string)
        string = re.sub(r'[\]\}]', ')', string)
        return encode(string)

    def __repr__(self):
        """
        Prints the name of the website.
        """
        return "'Lyrics Wiki' website"