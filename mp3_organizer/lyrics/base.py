__author__ = 'Ofir'

import re
import urllib


class Grabber(object):
    """
    Supplies simple functions for finding lyrics.
    """

    MAX_RESULTS = 1

    def __init__(self, verbose=True):
        """
        Initializes the lyrics grabber.
        :param verbose: Whether or not to print output.
        :type verbose: bool.
        """
        self.verbose = verbose

    @staticmethod
    def get_name():
        return "Unknown"

    def find_lyrics(self, track, artist=None, album=None, prompt=True, web=True):
        """
        Searches website for the track and returns its lyrics.
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
        :returns: The tracks' lyrics, or None.
        """
        raise NotImplementedError("Grabber didn't implement this method.")

    def __repr__(self):
        """
        Prints the name of the website.
        """
        return "Unknown website"

    def _prompt_user(self, track, album, artist):
        """
        Prompts the user and asks for result verification.
        :param track: The result track's title.
        :type track: str.
        :param album: The result album.
        :type album: str.
        :param artist: The result artist.
        :type artist: str.
        :return: The user's answer (y/n).
        """
        question = "Found track '" + track + "' from album '" + album + "' by '" + \
                   artist + "'. Is this correct (y/n)?"
        user_answer = raw_input(question)
        while not user_answer in ['y', 'n']:
            print "Please enter either 'y' or 'n'."
            user_answer = raw_input(question)
        return user_answer