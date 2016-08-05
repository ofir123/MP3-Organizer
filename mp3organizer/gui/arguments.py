class Arguments(object):
    """
    A dummy arguments class to run the organizer with.
    """

    def __init__(self, path, album, artist, genre, image, client, grabber):
        """
        Receives all the required running parameters and saves them.

        :param path: The files' path.
        :param album: The album's title.
        :param artist: The artist's name.
        :param genre: The album's genre.
        :param image: The path to save the album's artwork in.
        :param client: The preferred client to use.
        :param grabber: The preferred lyrics grabber to use.
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
