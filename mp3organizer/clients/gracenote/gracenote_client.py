import urllib.request

import logbook

from .gracenote_api import GracenoteAPI
from .gracenote_account import CLIENT_ID, USER_ID
from ..base import Client, ConnectionException
from mp3organizer.datatypes.album import Album
from mp3organizer.datatypes.track import Track

logger = logbook.Logger('GracenoteClient')


class GracenoteClient(Client):
    """
    Supplies simple functions for finding an album in Gracenote.
    """

    @staticmethod
    def get_name():
        return 'Gracenote'

    def connect(self):
        """
        Initializes the Gracenote proxy object, which simulates a connection.
        """
        if self.verbose:
            logger.info('Connecting to the Gracenote service...')
        self.api = GracenoteAPI(CLIENT_ID, USER_ID)
        self._connected = True
        if self.verbose:
            logger.debug('Connection successful!')

    def find_album(self, album, artist=None, prompt=True, web=False):
        """
        Searches Gracenote for the artist and returns the album data.

        :param album: The album's name.
        :param artist: The artist's name.
        :param prompt: Whether or not to prompt the user for approval.
        :param web: Whether or not to open a browser with the album's information.
        :returns: album or None.
        """
        if not self.is_connected():
            raise ConnectionException('Connection wasn\'t initialized')
        if web:
            logger.debug('Web not supported in Gracenote.')

        results = self.api.search_album(album, artist)
        if self.verbose:
            logger.info('Found {} results.'.format(len(results)))
        for result in results:
            try:
                # If any of these attributes doesn't exist, an exception will be raised.
                tracks_list = self._get_tracks_list(result)
                result_artist = result[GracenoteAPI.ARTIST_NAME].capitalize()
                result_album = result[GracenoteAPI.ALBUM_TITLE].capitalize()
                # Confirm with the user.
                if prompt:
                    user_answer = self._prompt_user(result_album, result_artist)
                else:
                    user_answer = 'y'
                if user_answer == 'y':
                    if self.verbose:
                        logger.debug('Getting more info on result: {} by {}'.format(result_album, result_artist))
                    # Get extra data and return the result.
                    result_year = result[GracenoteAPI.ALBUM_YEAR]
                    image_data = urllib.request.urlopen(result[GracenoteAPI.ALBUM_ART_URL]).read()
                    result_artwork = None
                    if self.artwork_folder:
                        result_artwork = self._save_image(image_data, album)
                        if self.verbose:
                            logger.debug('Artwork found!')
                    if self.verbose:
                        logger.debug('Finished extracting information from the service.')
                    return Album(album, artist or result_artist, artwork_path=result_artwork,
                                 year=result_year, tracks_list=tracks_list)
            except KeyError:
                # This result didn't not contain all the necessary information.
                logger.warning('Bad result, moving on to the next one...')

        return None

    def __repr__(self):
        """
        Prints the name of the service.
        """
        return 'Gracenote service'

    @staticmethod
    def _get_tracks_list(result):
        """
        Retrieves the tracks list from the results object.

        :param result: The result object.
        :return: An ordered list of Track objects.
        """
        tracks_list = []
        for track_info in result[GracenoteAPI.TRACKS]:
            tracks_list.append(Track(track_info[GracenoteAPI.TRACK_NUMBER], track_info[GracenoteAPI.TRACK_TITLE]))
        return tracks_list
