__author__ = 'Ofir'

import webbrowser
import urllib2
from amazon_api import AmazonAPI
from mp3_organizer.clients.amazon.amazon_account import ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG
from mp3_organizer.clients.base import Client, ConnectionException
from mp3_organizer.types.album import Album
from mp3_organizer.types.track import Track


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
        if self.verbose:
            print "Connecting to the Amazon service..."
        self.amazon = AmazonAPI(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG)
        self._connected = True
        if self.verbose:
            print "Connection successful!"

    def find_album(self, album, artist=None, prompt=True, web=True):
        """
        Searches Amazon for the artist and returns the album data.
        :param album: The album's name.
        :type album: str.
        :param artist: The artist's name.
        :type artist: str.
        :param prompt: Whether or not to prompt the user for approval.
        :type prompt: bool.
        :param web: Whether or not to open a browser with the album's information.
        :type web: bool.
        :returns: album or None.
        """
        if not self.is_connected():
            raise ConnectionException("Connection wasn't initialized")

        search_string = album
        if artist:
            search_string += " " + artist
        results = self.amazon.search_items_limited(limit=Client.MAX_RESULTS, Keywords=search_string,
                                                   SearchIndex=AmazonClient.SEARCH_INDEX)
        if self.verbose:
            print "Found " + str(len(results)) + " results."
        for result in results:
            try:
                # If any of these attributes doesn't exist, an exception will be raised.
                tracks_list = self._get_tracks_list(result)
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
                    user_answer = self._prompt_user(result_album, result_artist)
                else:
                    user_answer = 'y'
                if user_answer == 'y':
                    if self.verbose:
                        print "Getting more info on result: " + result_album + \
                              " by " + result_artist
                    # Get extra data and return the result.
                    result_year = self._get_release_year(result.item.ItemAttributes.ReleaseDate.text)
                    image_data = urllib2.urlopen(result.item.LargeImage.URL.text).read()
                    result_artwork = None
                    if self.artwork_folder:
                        result_artwork = self._save_image(image_data, result_album)
                        if self.verbose:
                            print "Artwork found!"
                    if self.verbose:
                        print "Finished extracting information from the service."
                    return Album(result_album, result_artist, artwork_path=result_artwork,
                                 year=result_year, tracks_list=tracks_list)
            except AttributeError:
                # This result wasn't an Audio CD. Move on to the next result.
                print "Bad result, moving on to the next one..."

        return None

    def __repr__(self):
        """
        Prints the name of the service.
        """
        return "Amazon service"

    def _get_release_year(self, release_date):
        """
        Extracts the album's release year from its release date.
        :param release_date: The album's release date, in format 'YYYY-MM-DD'.
        :return: str
        """
        return release_date[:4]

    def _get_tracks_list(self, result):
        """
        Retrieves the tracks list from the results object.
        :param result: An ordered list of the track names.
        :type result: list.
        :return: An ordered list of Track objects.
        """
        tracks_list = []
        for track_number, track_name in enumerate(result.item.Tracks.Disc.getchildren()):
            tracks_list.append(Track(track_number+1, track_name.text))
        return tracks_list