import os

from mp3organizer.file_utils import normalize_name


class ConnectionException(Exception):
    """
    Raised when connection wasn't initialized before first use.
    """
    pass


class Client(object):
    """
    Supplies simple functions for finding an album.
    """

    MAX_RESULTS = 1
    ARTWORK_EXTENSION = '.jpg'

    def __init__(self, artwork_folder=None, verbose=True):
        """
        Initializes the client.

        :param artwork_folder: The folder to save pictures in.
        :param verbose: Whether or not to print output.
        """
        self.api = None
        self.artwork_folder = artwork_folder
        self.verbose = verbose
        self._connected = False

    @staticmethod
    def get_name():
        return 'Unknown'

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
        raise NotImplementedError('Client didn\'t implement this method.')

    def find_album(self, album, artist=None, prompt=True, web=True):
        """
        Searches service for the artist and returns the album data.

        :param album: The album's name.
        :param artist: The artist's name.
        :param prompt: Whether or not to prompt the user for approval.
        :param web: Whether or not to open a browser with the album's information.
        :returns: album or None.
        """
        raise NotImplementedError('Client didn\'t implement this method.')

    def __repr__(self):
        """
        Prints the name of the service.
        """
        return 'Unknown service'

    @staticmethod
    def _prompt_user(album, artist):
        """
        Prompts the user and asks for result verification.

        :param album: The result album.
        :param artist: The result artist.
        :return: The user's answer (True or False).
        """
        question = 'Found album "{}" by "{}". Is this correct (y/n)?'.format(album, artist)
        user_answer = input(question)
        while user_answer not in ['y', 'n']:
            print('Please enter either "y" or "n".')
            user_answer = input(question)
        return user_answer == 'y'

    def _save_image(self, image_data, album):
        """
        Saves the album's artwork.

        :param image_data: The image to write.
        :param album: The album's name.
        :return: The artwork's path.
        """
        normalized_album = normalize_name(album)
        album = ' '.join(x.capitalize() for x in normalized_album.split(' '))
        image_path = os.path.join(self.artwork_folder, album + Client.ARTWORK_EXTENSION)
        image_file = open(image_path, 'wb')
        image_file.write(image_data)
        image_file.close()
        return image_path
