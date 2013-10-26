__author__ = 'Halti'

import os.path


class PathException(Exception):
    """
    Thrown when an invalid album path was given.
    """
    pass


def get_mime_type(filename):
    """
    Finds out the mime type for the given image file.
    :param filename: The file to check.
    :type filename: str.
    :return: The mime string, or None if not supported.
    """
    extension = os.path.splitext(filename)[1]
    if extension == ".png":
        return 'image/png'
    if extension == ".jpg" or extension == ".jpeg":
        return 'image/jpeg'
    return None


def normalize_name(filename):
    """
    normalizes the file name by stripping spaces, converting to lower case,
    and removing '_' characters (which don't work with the '\b' option in re).
    :param filename: The file's name.
    :type filename: str.
    :return: The normalized filename.
    """
    return filename.strip().lower().replace("_", " ").replace(".", " ").replace("-", " ")


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