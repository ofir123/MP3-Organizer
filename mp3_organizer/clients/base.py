__author__ = 'Ofir'

import os


class ConnectionException(Exception):
    """
    Thrown when connection wasn't initialized before first use.
    """
    pass


class Client(object):
    """
    Supplies simple functions for finding an album.
    """

    MAX_RESULTS = 1
    ARTWORK_EXTENSION = ".jpg"

    def __init__(self, artwork_folder=None, verbose=True):
        """
        Initializes the Amazon client.
        :param artwork_folder: The folder to save pictures in.
        :type artwork_folder: str.
        :param verbose: Whether or not to print output.
        :type verbose: bool.
        """
        self.api = None
        self.artwork_folder = artwork_folder
        self.verbose = verbose
        self._connected = False

    @property
    def name(self):
        return "Unknown"

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
        :returns: album or None.
        """
        raise NotImplementedError("Client didn't implement this method.")

    def __repr__(self):
        """
        Prints the name of the service.
        """
        return "Unknown service"

    def _prompt_user(self, album, artist):
        """
        Prompts the user and asks for result verification.
        :param album: The result album.
        :type album: str.
        :param artist: The result artist.
        :type artist: str.
        :return: The user's answer (y/n).
        """
        user_answer = raw_input("Found album '" + album + "' by '" +
                                artist + "'. Is this correct (y/n)?")
        while not user_answer in ['y', 'n']:
            print "Please enter either 'y' or 'n'."
            user_answer = raw_input("Found album '" + album + "' by '" +
                                    artist + "'. Is this correct (y/n)?")
        return user_answer

    def _save_image(self, image_data, album):
        """
        Saves the album's artwork.
        :param image_data: The image to write.
        :type image_data: binary.
        :param album: The album's name.
        :type album: str.
        :return: The artwork's path.
        """
        image_path = os.path.join(self.artwork_folder, album + Client.ARTWORK_EXTENSION)
        image_file = open(image_path, 'wb')
        image_file.write(image_data)
        image_file.close()
        return image_path