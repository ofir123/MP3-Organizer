__author__ = 'Ofir'


class Arguments(object):
    """
    A dummy arguments class to run the organizer with.
    """

    def __init__(self, path, album, artist, genre, image, client, grabber):
        """
        Receives all the required running parameters and saves them.
        :param path: The files' path.
        :type path: str.
        :param album: The album's title.
        :type path: str.
        :param artist: The artist's name.
        :type path: str.
        :param genre: The album's genre.
        :type path: str.
        :param image: The path to save the album's artwork in.
        :type path: str.
        :param client: The preferred client to use.
        :type path: str.
        :param grabber: The preferred lyrics grabber to use.
        :type path: str.
        """
        self.path = path
        self.album = album
        self.artist = artist
        self.genre = genre
        self.image_path = image
        self.client = client
        self.grabber = grabber
        self.verbose = True
        self.prompt = False
        self.web = True