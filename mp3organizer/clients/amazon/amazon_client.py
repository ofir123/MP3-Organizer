import webbrowser
import urllib.request

import logbook

from .amazon_api import AmazonAPI
from .amazon_account import ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG
from ..base import Client, ConnectionException
from mp3organizer.datatypes.album import Album
from mp3organizer.datatypes.track import Track

logger = logbook.Logger('AmazonClient')


class AmazonClient(Client):
    """
    Supplies simple functions for finding an album in Amazon.
    """

    SEARCH_INDEX = 'Music'
    VALID_BINDINGS = ['Audio CD', 'Vinyl']

    @staticmethod
    def get_name():
        return 'Amazon'

    def connect(self):
        """
        Initializes the Amazon proxy object, which simulates a connection.
        """
        if self.verbose:
            logger.info('Connecting to the Amazon service...')
        self.api = AmazonAPI(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG)
        self._connected = True
        if self.verbose:
            logger.debug('Connection successful!')

    def find_album(self, album, artist=None, prompt=True, web=True):
        """
        Searches Amazon for the artist and returns the album data.

        :param album: The album's name.
        :param artist: The artist's name.
        :param prompt: Whether or not to prompt the user for approval.
        :param web: Whether or not to open a browser with the album's information.
        :returns: album or None.
        """
        if not self.is_connected():
            raise ConnectionException('Connection wasn\'t initialized')

        search_string = album
        if artist:
            search_string += ' {}'.format(artist)
        results = self.api.search_items_limited(limit=Client.MAX_RESULTS, Keywords=search_string,
                                                SearchIndex=AmazonClient.SEARCH_INDEX)
        if self.verbose:
            logger.info('Found {} results.'.format(len(results)))
        for result in results:
            try:
                # If any of these attributes doesn't exist, an exception will be raised.
                tracks_list = self._get_tracks_list(result)
                result_artist = result.item.ItemAttributes.Artist.text.capitalize()
                result_album = result.title.capitalize()
                # Check if the result is an album.
                if result.item.ItemAttributes.Binding not in AmazonClient.VALID_BINDINGS:
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
                        logger.debug('Getting more info on result: {} by {}'.format(result_album, result_artist))
                    # Get extra data and return the result.
                    result_year = self._get_release_year(result.item.ItemAttributes.ReleaseDate.text)
                    try:
                        image_data = urllib.request.urlopen(result.item.LargeImage.URL.text).read()
                        result_artwork = None
                        if self.artwork_folder:
                            result_artwork = self._save_image(image_data, album)
                            if self.verbose:
                                logger.debug('Artwork found!')
                    except AttributeError:
                        logger.debug('Artwork not found!')
                        result_artwork = None
                    if self.verbose:
                        logger.debug('Finished extracting information from the service.')
                    return Album(album, artist or result_artist, artwork_path=result_artwork,
                                 year=result_year, tracks_list=tracks_list)
            except AttributeError as ex:
                # This result wasn't an Audio CD. Move on to the next result.
                logger.warning('Bad result ({}), moving on to the next one...'.format(ex))

        return None

    def __repr__(self):
        """
        Prints the name of the service.
        """
        return 'Amazon service'

    @staticmethod
    def _get_release_year(release_date):
        """
        Extracts the album's release year from its release date.

        :param release_date: The album's release date, in format 'YYYY-MM-DD'.
        """
        return release_date[:4]

    @staticmethod
    def _get_tracks_list(result):
        """
        Retrieves the tracks list from the results object (supports multiple discs).

        :param result: An ordered list of the track names.
        :return: An ordered list of Track objects.
        """
        tracks_list = []
        current_disc = result.item.Tracks.Disc
        multiple_discs = True if current_disc.getnext() is not None else False
        disc_num = 1 if multiple_discs else None
        while current_disc is not None:
            for track_number, track_name in enumerate(current_disc.getchildren()):
                tracks_list.append(Track(track_number+1, track_name.text, disc_num))
            current_disc = current_disc.getnext()
            if current_disc is not None:
                disc_num += 1
        return tracks_list
