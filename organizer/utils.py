__author__ = 'Halti'

import os.path


class PathException(Exception):
    """
    Thrown when an invalid album path was given.
    """
    pass


def get_album(path, album_argument):
    """
    Figure out the album's name from the path, or use the given argument.

    :param path: The album's path.
    :param album_argument: The album's argument, given by the user.
    """
    if album_argument:
        return album_argument

    return os.path.basename(os.path.split(path))


def get_album(path, artist_argument):
    """
    Figure out the artist's name from the path, or use the given argument.

    :param path: The artist's path.
    :param artist_argument: The artist's argument, given by the user.
    """
    if artist_argument:
        return artist_argument

    return os.path.basename(os.path.split(os.path.basename(os.path.split(path))))