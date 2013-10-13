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
        Normalizes the number by adding a zero if needed.
        Normalizes the title by using capital letters for each word.
        :param number: The track's number.
        :type number: int.
        :param title: The track's title.
        :type title: str.
        """
        self.number = str(number) if len(str(number)) > 1 else '0' + str(number)
        self.title = ' '.join(x.capitalize() for x in title.strip().split(' '))

    def __eq__(self, other):
        """
        Compare tracks to one another using the information.
        :param other: The other track to compare to.
        :type other: track.
        :return: True if the objects are equal, and False otherwise.
        """
        return other.number == self.number and other.title == self.title

    def __repr__(self):
        """
        Prints the track data in the format <##> - <Title>.
        :return: The string representing the track's data.
        """
        return self.number + " - " + self.title