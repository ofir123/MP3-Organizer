__author__ = 'Ofir'

import urllib2
from gracenote_api import GracenoteAPI
from gracenote_account import CLIENT_ID, USER_ID
from mp3_organizer.clients.base import Client, ConnectionException
from mp3_organizer.datatypes.album import Album
from mp3_organizer.datatypes.track import Track


class GracenoteClient(Client):
    """
    Supplies simple functions for finding an album in Gracenote.
    """

    @property
    def name(self):
        return "Gracenote"

    def connect(self):
        """
        Initializes the Gracenote proxy object, which simulates a connection.
        """
        if self.verbose:
            print "Connecting to the Gracenote service..."
        self.api = GracenoteAPI(CLIENT_ID, USER_ID)
        self._connected = True
        if self.verbose:
            print "Connection successful!"

    def find_album(self, album, artist=None, prompt=True, web=False):
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
        if web:
            print "Web not supported in Gracenote."

        results = self.api.search_album(album, artist)
        if self.verbose:
            print "Found " + str(len(results)) + " results."
        for result in results:
            try:
                # If any of these attributes doesn't exist, an exception will be raised.
                tracks_list = self._get_tracks_list(result)
                result_artist = result[GracenoteAPI.ARTIST_NAME]
                result_album = result[GracenoteAPI.ALBUM_TITLE]
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
                    result_year = result[GracenoteAPI.ALBUM_YEAR]
                    image_data = urllib2.urlopen(result[GracenoteAPI.ALBUM_ART_URL]).read()
                    result_artwork = None
                    if self.artwork_folder:
                        result_artwork = self._save_image(image_data, result_album)
                        if self.verbose:
                            print "Artwork found!"
                    if self.verbose:
                        print "Finished extracting information from the service."
                    return Album(result_album, result_artist, artwork_path=result_artwork,
                                 year=result_year, tracks_list=tracks_list)
            except KeyError:
                # This result didn't not contain all the necessary information.
                print "Bad result, moving on to the next one..."

        return None

    def __repr__(self):
        """
        Prints the name of the service.
        """
        return "Gracenote service"

    def _get_tracks_list(self, result):
        """
        Retrieves the tracks list from the results object.
        :param result: The result object.
        :type result: dict.
        :return: An ordered list of Track objects.
        """
        tracks_list = []
        for track_info in result[GracenoteAPI.TRACKS]:
            tracks_list.append(Track(track_info[GracenoteAPI.TRACK_NUMBER],
                                     track_info[GracenoteAPI.TRACK_TITLE]))
        return tracks_list