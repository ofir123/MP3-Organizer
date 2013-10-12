__author__ = 'Halti'

import os.path
from organizer import OrganizerException


class PathException(OrganizerException):
    """
    Thrown when an invalid album path was given.
    """
    pass


def get_album(path, album_argument=None):
    """
    Figure out the album's name from the path, or use the given argument.

    :param path: The album's path.
    :param album_argument: The album's argument, given by the user.
    :returns: The album's name.
    :raises: PathException if the path was invalid.
    """
    if album_argument:
        album = album_argument
    else:
        album = os.path.basename(path)
    if album == "":
        raise PathException("Path does not include album name")
    return album


def get_artist(path, artist_argument=None):
    """
    Figure out the artist's name from the path, or use the given argument.

    :param path: The artist's path.
    :param artist_argument: The artist's argument, given by the user.
    :returns: The artist's name.
    :raises: PathException if the path was invalid.
    """
    if artist_argument:
        artist = artist_argument
    else:
        artist = os.path.basename(os.path.dirname(path))
    if artist == "":
        raise PathException("Path does not include artist name")
    return artist