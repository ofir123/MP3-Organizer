__author__ = 'Halti'


class Album(object):
    """
    A POJO class to hold all the album data.
    Contains the following information:
    Name, Artist, Genre, Year and Artwork (as path).
    """

    def __init__(self, name, artist, genre=None, year=None,
                 artwork_path=None, tracks_list=None):
        """
        Initializes the album data object.
        :param name: The album's name.
        :type name: str.
        :param artist: The artist's name.
        :type artist: str.
        :param genre: The album's genre.
        :type genre: str.
        :param year: The album's release year.
        :type year: int.
        :param artwork_path: The artwork's file path.
        :type artwork_path: str.
        :param tracks_list: The tracks_list.
        :type tracks_list: list.
        """
        self.name = name
        self.artist = artist
        self.genre = genre
        self.year = year
        self.artwork_path = artwork_path
        self.tracks_list = tracks_list

    def __repr__(self):
        """
        Prints the album data in the format <Artist> - <Album>.
        :return: The string representing the album's data.
        """
        return self.artist + " - " + self.name
