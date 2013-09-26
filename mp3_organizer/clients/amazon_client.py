__author__ = 'Ofir'

import webbrowser
import os.path
import urllib2
from amazon.api import AmazonAPI
from amazon_account import ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG
from mp3_organizer.types.album import Album
from base import Client, ConnectionException


class AmazonClient(Client):
    """
    Supplies simple functions for finding an album in Amazon.
    """

    SEARCH_INDEX = "Music"
    ALBUM_BINDING = "Audio CD"

    def connect(self):
        """
        Initializes the Amazon proxy object, which simulates a connection.
        """
        self.amazon = AmazonAPI(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG)
        self._connected = True

    def find_album(self, album, artist=None, prompt=True, web=True):
        """
        Searches Amazon for the artist and returns the album data.
        :param album: The album's name.
        :type album: str.
        :param artist: The artist's name.
        :type artist: str.
        :param prompt: Whether or not to prompt the user for approval.
        :type prompt: bool.
        :param web: Whether or not to open a browser with the album's informaion.
        :type web: bool.
        :returns: album.
        """
        if not self.is_connected():
            raise ConnectionException("Connection wasn't initialized")

        search_string = album
        if artist:
            search_string += " " + artist
        results = self.amazon.search_n(Client.MAX_RESULTS, Keywords=search_string,
                                       SearchIndex=AmazonClient.SEARCH_INDEX)
        for result in results:
            try:
                # If any of these attributes doesn't exist, an exception will be raised.
                tracks_list = result.item.Tracks.Disc.getchildren()
                result_artist = result.item.ItemAttributes.Artist
                result_album = result.title
                # Check if the result is an album.
                if result.item.ItemAttributes.Binding != AmazonClient.ALBUM_BINDING:
                    continue
                # Open the item's web page in a new tab, to help the user.
                if web:
                    webbrowser.open(result.item.DetailPageURL.text, new=2)
                # Confirm with the user.
                if prompt:
                    user_answer = raw_input("Found album '" + result_album + "' by '" +
                                            result_artist + "'. Is this correct (y/n)?")
                    while not user_answer in ['y', 'n']:
                        print "Please enter either 'y' or 'n'."
                        user_answer = raw_input("Found album '" + result_album + "' by '" +
                                                result_artist + "'. Is this correct (y/n)?")
                else:
                    user_answer = 'y'
                if user_answer == 'y':
                    # Get extra data and return the result.
                    result_year = self._get_release_year(result.item.ItemAttributes.ReleaseDate.text)
                    image_data = urllib2.urlopen(result.item.LargeImage.URL.text).read()
                    result_artwork = None
                    if self.artwork_folder:
                        result_artwork = self._save_image(image_data, result_album)
                    return Album(result_album, result_artist, artwork_path=result_artwork,
                                 year=result_year, tracks_list=tracks_list)
            except AttributeError:
                # This result wasn't an Audio CD. Move on to the next result.
                pass

        return None

    def _save_image(self, image_data, album):
        """
        Saves the album's artwork.
        :param image_data: The image to write.
        :type image_data: binary.
        :param album: The album's name.
        :type album: str.
        :return: The artwork's path.
        """
        image_path = os.path.join(self.artwork_folder, album + Client.ARTWORK_EXTENSION)
        image_file = open(image_path, 'wb')
        image_file.write(image_data)
        image_file.close()
        return image_path

    def _get_release_year(self, release_date):
        """
        Extracts the album's release year from its release date.
        :param release_date: The album's release date, in format 'YYYY-MM-DD'.
        :return: str
        """
        return release_date[:4]