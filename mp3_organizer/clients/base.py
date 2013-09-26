__author__ = 'Ofir'


class ConnectionException(Exception):
    """
    Thrown when connection wasn't initialized before first use.
    """
    pass


class Client(object):
    """
    Supplies simple functions for finding an album.
    """

    MAX_RESULTS = 10
    ARTWORK_EXTENSION = ".jpg"

    def __init__(self, artwork_folder=None):
        """
        Initializes the Amazon client.
        :param artwork_folder: The folder to save pictures in.
        :type artwork_folder: str.
        """
        self.artwork_folder = artwork_folder
        self._connected = False

    def is_connected(self):
        """
        Checks if the client is connected.
        :return: True if connected, False otherwise.
        """
        return self._connected

    def connect(self):
        """
        Initializes the connection to the service.
        """
        raise NotImplementedError("Client didn't implement this method.")

    def find_album(self, album, artist=None, prompt=True, web=True):
        """
        Searches service for the artist and returns the album data.
        :param album: The album's name.
        :type album: str.
        :param artist: The artist's name.
        :type artist: str.
        :param prompt: Whether or not to prompt the user for approval.
        :type prompt: bool.
        :param web: Whether or not to open a browser with the album's information.
        :type web: bool.
        :returns: album.
        """
        raise NotImplementedError("Client didn't implement this method.")