class Album(object):
    """
    A POPO class to hold all the album data.
    Contains the following information:
    Name, Artist, Genre, Year and Artwork (as path).
    """

    def __init__(self, name, artist, genre=None, year=None,
                 artwork_path=None, tracks_list=None):
        """
        Initializes the album data object.

        :param name: The album's name.
        :param artist: The artist's name.
        :param genre: The album's genre.
        :param year: The album's release year.
        :param artwork_path: The artwork's file path.
        :param tracks_list: The tracks_list.
        """
        self.name = ' '.join(x.capitalize() for x in name.strip().split(' '))
        self.artist = ' '.join(x.capitalize() for x in artist.strip().split(' '))
        self.genre = genre
        self.year = year
        self.artwork_path = artwork_path
        self.tracks_list = tracks_list

    def __eq__(self, other):
        """
        Compare albums to one another using the information.

        :param other: The other track to compare to.
        :return: True if the objects are equal, and False otherwise.
        """
        return other.name == self.name and other.artist == self.artist and \
            other.genre == self.genre and other.year == self.year and \
            other.artwork_path == self.artwork_path and other.tracks_list == self.tracks_list

    def __repr__(self):
        """
        Prints the album data in the format <Artist> - <Album>.

        :return: The string representing the album's data.
        """
        return '{} - {}'.format(self.artist, self.name)
