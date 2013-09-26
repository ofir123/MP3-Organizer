__author__ = 'Halti'


class Track(object):
    """
    A POJO class to hold all the track data.
    Contains the following information:
    Number and Title.
    """

    def __init__(self, number, title):
        """
        Initializes the track data object.
        :param number: The track's number.
        :type number: int.
        :param title: The track's title.
        :type title: str.
        """
        self.number = number
        self.title = title
