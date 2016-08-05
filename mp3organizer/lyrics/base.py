class Grabber(object):
    """
    Supplies simple functions for finding lyrics.
    """

    MAX_RESULTS = 1

    def __init__(self, verbose=True):
        """
        Initializes the lyrics grabber.

        :param verbose: Whether or not to print output.
        """
        self.verbose = verbose

    @staticmethod
    def get_name():
        return 'Unknown'

    def find_lyrics(self, track, artist, album):
        """
        Searches website for the track and returns its lyrics.

        :param track: The track's title.
        :param artist: The artist's name.
        :param album: The album's name.
        :returns: The tracks' lyrics, or None.
        """
        raise NotImplementedError('Grabber didn\'t implement this method.')

    def __repr__(self):
        """
        Prints the name of the website.
        """
        return 'Unknown website'

    @staticmethod
    def _prompt_user(track, album, artist):
        """
        Prompts the user and asks for result verification.

        :param track: The result track's title.
        :param album: The result album.
        :param artist: The result artist.
        :return: The user's answer (True or False).
        """
        question = 'Found track "{}" from album "{}" by "{}". Is this correct (y/n)?'.format(track, album, artist)
        user_answer = input(question)
        while user_answer not in ['y', 'n']:
            print('Please enter either "y" or "n".')
            user_answer = input(question)
        return user_answer == 'y'
