__author__ = 'Ofir'

import webbrowser
from amazon.api import AmazonAPI
from account import ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG


class ConnectionException(Exception):
    """
    Thrown when connection wasn't initialized before first use.
    """
    pass


class AmazonClient(object):
    """
    Supplies simple functions for finding an album in Amazon.
    """

    MAX_RESULTS = 10
    SEARCH_INDEX = "Music"

    def __init__(self):
        self._connected = False

    def is_connected(self):
        return self._connected

    def connect(self):
        """
        Initializes the Amazon proxy object, which simulates a connection.
        """
        self.amazon = AmazonAPI(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG)
        self._connected = True

    def find_album(self, album, artist=None, prompt=True, web=True):
        """
        Searches Amazon for the artist and returns the results.

        :param album: The album's name.
        :type album: str.
        :param artist: The artist's name.
        :type artist: str.
        :param prompt: Whether or not to prompt the user for approval.
        :type prompt: bool.
        :param web: Whether or not to open a browser with the album's informaion.
        :type web: bool.
        :returns: list -- the ordered list of tracks in the given album,
                          or None if no album was found.
        """
        if not self.is_connected():
            raise ConnectionException("Connection wasn't initialized")

        search_string = album
        if artist:
            search_string += " " + artist
        results = self.amazon.search_n(self.MAX_RESULTS, Keywords=search_string,
                                       SearchIndex=self.SEARCH_INDEX)
        for result in results:
            try:
                # If any of these attributes doesn't exist, an exception will be raised.
                tracks_list = result.item.Tracks.Disc.getchildren()
                result_artist = result.item.ItemAttributes.Artist
                result_album = result.title
                # Open the item's web page in a new tab, to help the user.
                if web:
                    webbrowser.open(result.item.DetailPageURL.text, new=2)
                # Confirm with the user.
                if prompt:
                    user_answer = raw_input("Found album '" + result_album + "' by '" +
                                            result_artist + "'. Is this correct (y/n)?")
                    while not user_answer in ['y', 'n']:
                        print "Please enter either 'y' or 'n'."
                        user_answer = raw_input("Found album '" + result_album + "' by '" +
                                                result_artist + "'. Is this correct (y/n)?")
                else:
                    user_answer = 'y'
                if user_answer == 'y':
                    return tracks_list
            except AttributeError:
                # This result wasn't an Audio CD. Move on to the next result.
                pass

        return None



