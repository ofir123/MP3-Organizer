__author__ = 'Halti'


class Track(object):
    """
    A POJO class to hold all the track data.
    Contains the following information:
    Number, Title and Disc Number.
    """

    def __init__(self, number, title, disc_num=None):
        """
        Initializes the track data object.
        Normalizes the number by adding a zero if needed.
        Normalizes the title by using capital letters for each word.
        :param number: The track's number.
        :type number: int.
        :param title: The track's title.
        :type title: str.
        :param disc_num: The Disc number (if there are multiple discs in the album).
        :type disc_num: int.
        """
        self.number = str(number) if len(str(number)) > 1 else '0' + str(number)
        self.title = ' '.join(x.capitalize() for x in
                              title.replace('\\', ' - ').replace('/', ' - ').strip().split(' '))
        self.disc_num = disc_num

    def __eq__(self, other):
        """
        Compare tracks to one another using the information.
        :param other: The other track to compare to.
        :type other: track.
        :return: True if the objects are equal, and False otherwise.
        """
        return other.number == self.number and other.title == self.title and \
               other.disc_num == self.disc_num

    def __repr__(self):
        """
        Prints the track data in the format <##> - <Title>.
        :return: The string representing the track's data.
        """
        return self.number + " - " + self.title
