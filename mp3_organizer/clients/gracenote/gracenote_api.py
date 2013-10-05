import xml.etree.ElementTree
import urllib2
import urllib


class GracenoteAPI(object):
    """
    An API for querying the Amazon Web Service.
    """

    # Album consts.
    ALBUM_GNID = 'album_gnid'
    ALBUM_TITLE = 'album_title'
    ALBUM_YEAR = 'album_year'
    ALBUM_ART_URL = 'album_art_url'
    ALBUM_GENRE = 'genre'
    ALBUM_REVIEW_URL = 'review_url'

    # Artist consts.
    ARTIST_NAME = 'artist_name'
    ARTIST_IMAGE_URL = 'artist_image_url'
    ARTIST_BIO_URL = 'artist_bio_url'
    ARTIST_ORIGIN = 'artist_origin'
    ARTIST_ERA = 'artist_era'
    ARTIST_TYPE = 'artist_type'

    # Track consts.
    TRACKS = 'tracks'
    TRACK_NUMBER = 'track_number'
    TRACK_GNID = 'track_gnid'
    TRACK_TITLE = 'track_title'
    TRACK_ARTIST_NAME = 'track_artist_name'
    TRACK_MOOD = 'mood'
    TRACK_TEMPO = 'tempo'

    def __init__(self, client_id, user_id):
        """
        Initialize the Gracenote API Proxy.
        :param client_id: The Gracenote authentication key.
        :type client_id: str.
        :param user_id: The Gracenote user ID.
        :type user_id: str.
        """
        self.client_id = client_id
        self.user_id = user_id

    @staticmethod
    def get_gracenote_url(client_id):
        """
        Helper function to form URL to Gracenote service.
        """
        client_id_prefix = client_id.split('-')[0]
        return 'https://c' + client_id_prefix + '.web.cddbp.net/webapi/xml/1.0/'

    def search_track(self, artist, album, track=''):
        """
        Queries the Gracenote service for a specific track.
        :param artist: The artist's name.
        :type artist: str.
        :param album: The album's name.
        :type album: str.
        :param track: The track's name.
        :type track: str.
        :return: A list of name/value dictionaries with all the
        information (one for each result).
        """
        # Create XML request.
        query = GracenoteQuery()
        query.add_auth(self.client_id, self.user_id)
        query.add_query('ALBUM_SEARCH')
        query.add_query_mode('SINGLE_BEST_COVER')
        query.add_query_text_field('ARTIST', artist)
        query.add_query_text_field('ALBUM_TITLE', album)
        query.add_query_text_field('TRACK_TITLE', track)
        query.add_query_option('SELECT_EXTENDED', 'COVER,REVIEW,ARTIST_BIOGRAPHY,'
                               'ARTIST_IMAGE,ARTIST_OET,MOOD,TEMPO')
        query.add_query_option('SELECT_DETAIL', 'GENRE:3LEVEL,MOOD:2LEVEL,TEMPO:3LEVEL,'
                               'ARTIST_ORIGIN:4LEVEL,ARTIST_ERA:2LEVEL,ARTIST_TYPE:2LEVEL')
        query_xml = query.to_string()

        # POST query.
        response = urllib2.urlopen(GracenoteAPI.get_gracenote_url(self.client_id),
                                   query_xml)
        response_xml = response.read()
        # Parse response.
        results = []
        response_tree = xml.etree.ElementTree.fromstring(response_xml)
        response_elements = response_tree.findall('RESPONSE')
        for response_elem in response_elements:
            if response_elem.attrib['STATUS'] != 'OK':
                continue
            current_result = {}
            # Find Album element.
            album_elem = response_elem.find('ALBUM')
            # Parse album metadata.
            current_result[GracenoteAPI.ALBUM_GNID] = self._get_elem_text(album_elem, 'GN_ID')
            current_result[GracenoteAPI.ARTIST_NAME] = self._get_elem_text(album_elem, 'ARTIST')
            current_result[GracenoteAPI.ALBUM_TITLE] = self._get_elem_text(album_elem, 'TITLE')
            current_result[GracenoteAPI.ALBUM_YEAR] = self._get_elem_text(album_elem, 'DATE')
            current_result[GracenoteAPI.ALBUM_ART_URL] = self._get_elem_text(
                album_elem, 'URL', 'TYPE', 'COVERART')
            current_result[GracenoteAPI.ALBUM_GENRE] = self._get_multi_elem_text(
                album_elem, 'GENRE', 'ORD', 'ID')
            current_result[GracenoteAPI.ARTIST_IMAGE_URL] = self._get_elem_text(
                album_elem, 'URL', 'TYPE', 'ARTIST_IMAGE')
            current_result[GracenoteAPI.ARTIST_BIO_URL] = self._get_elem_text(
                album_elem, 'URL', 'TYPE', 'ARTIST_BIOGRAPHY')
            current_result[GracenoteAPI.ALBUM_REVIEW_URL] = self._get_elem_text(
                album_elem, 'URL', 'TYPE', 'REVIEW')

            # Look for OET.
            artist_origin_elem = album_elem.find('ARTIST_ORIGIN')
            if artist_origin_elem is not None:
                current_result[GracenoteAPI.ARTIST_ORIGIN] = self._get_multi_elem_text(
                    album_elem, 'ARTIST_ORIGIN', 'ORD', 'ID')
                current_result[GracenoteAPI.ARTIST_ERA] = self._get_multi_elem_text(
                    album_elem, 'ARTIST_ERA', 'ORD', 'ID')
                current_result[GracenoteAPI.ARTIST_TYPE] = self._get_multi_elem_text(
                    album_elem, 'ARTIST_TYPE', 'ORD', 'ID')
            else:
                # Try to get OET again by fetching album by GNID.
                current_result[GracenoteAPI.ARTIST_ORIGIN], \
                    current_result[GracenoteAPI.ARTIST_ERA], \
                    current_result[GracenoteAPI.ARTIST_TYPE] = \
                    self._get_oet(current_result[GracenoteAPI.ALBUM_GNID])

            # Parse tracks metadata.
            current_result[GracenoteAPI.TRACKS] = []
            track_elements = album_elem.findall('TRACK')
            for track_elem in track_elements:
                track_results = dict()
                track_results[GracenoteAPI.TRACK_NUMBER] = self._get_elem_text(track_elem, 'TRACK_NUM')
                track_results[GracenoteAPI.TRACK_GNID] = self._get_elem_text(track_elem, 'GN_ID')
                track_results[GracenoteAPI.TRACK_TITLE] = self._get_elem_text(track_elem, 'TITLE')
                track_results[GracenoteAPI.TRACK_ARTIST_NAME] = \
                    self._get_elem_text(track_elem, 'ARTIST')
                track_results[GracenoteAPI.TRACK_MOOD] = \
                    self._get_multi_elem_text(track_elem, 'MOOD', 'ORD', 'ID')
                track_results[GracenoteAPI.TRACK_TEMPO] = \
                    self._get_multi_elem_text(track_elem, 'TEMPO', 'ORD', 'ID')
                # If track-level GOET exists, overwrite metadata from album.
                if track_elem.find('GENRE') is not None:
                    track_results[GracenoteAPI.ALBUM_GENRE] = self._get_multi_elem_text(
                        track_elem, 'GENRE', 'ORD', 'ID')
                if track_elem.find('ARTIST_ORIGIN') is not None:
                    track_results[GracenoteAPI.ARTIST_ORIGIN] = self._get_multi_elem_text(
                        track_elem, 'ARTIST_ORIGIN', 'ORD', 'ID')
                if track_elem.find('ARTIST_ERA') is not None:
                    track_results[GracenoteAPI.ARTIST_ERA] = self._get_multi_elem_text(
                        track_elem, 'ARTIST_ERA', 'ORD', 'ID')
                if track_elem.find('ARTIST_TYPE') is not None:
                    track_results[GracenoteAPI.ARTIST_TYPE] = self._get_multi_elem_text(
                        track_elem, 'ARTIST_TYPE', 'ORD', 'ID')
                current_result[GracenoteAPI.TRACKS].append(track_results)

            results.append(current_result)

        return results

    def search_album(self, album, artist):
        """
        Queries the Gracenote service for a specific album.
        :param album: The album's name.
        :type album: str.
        :param artist: The artist's name.
        :type artist: str.
        """
        return self.search_track(artist, album)

    def _get_oet(self, gnid):
        """
        Helper function to retrieve Origin, Era, and Artist Type by direct album fetch.
        :param gnid: The GNID.
        :type gnid: str.
        :return: origin, era and artist, or None if an error occurred.
        """
        # Create XML request.
        query = GracenoteQuery()

        query.add_auth(self.client_id, self.user_id)
        query.add_query('ALBUM_FETCH')
        query.add_query_gnid(gnid)
        query.add_query_option('SELECT_EXTENDED', 'ARTIST_OET')
        query.add_query_option('SELECT_DETAIL',
                               'ARTIST_ORIGIN:4LEVEL,ARTIST_ERA:2LEVEL,ARTIST_TYPE:2LEVEL')
        query_xml = query.to_string()

        # POST query.
        response = urllib2.urlopen(GracenoteAPI.get_gracenote_url(self.client_id), query_xml)
        album_xml = response.read()

        # Parse XML
        responseTree = xml.etree.ElementTree.fromstring(album_xml)
        response_elem = responseTree.find('RESPONSE')
        if response_elem.attrib['STATUS'] == 'OK':
            album_elem = response_elem.find('ALBUM')
            artist_origin = self._get_multi_elem_text(album_elem, 'ARTIST_ORIGIN', 'ORD', 'ID')
            artist_era = self._get_multi_elem_text(album_elem, 'ARTIST_ERA', 'ORD', 'ID')
            artist_type = self._get_multi_elem_text(album_elem, 'ARTIST_TYPE', 'ORD', 'ID')
            return artist_origin, artist_era, artist_type
        return None

    def _get_elem_text(self, parent_elem, elem_name, elem_attribute_name=None,
                       elem_attribute_value=None):
        """
        XML parsing helper function to find child element with a specific name,
        and return the text value.
        """
        elements = parent_elem.findall(elem_name)
        for elem in elements:
            if elem_attribute_name is not None and elem_attribute_value is not None:
                if elem.attrib[elem_attribute_name] == elem_attribute_value:
                    return urllib.unquote(elem.text)
                else:
                    continue
            else:
                # Just return the first one.
                return urllib.unquote(elem.text)
        return ''

    def _get_elem_attribute(self, parent_elem, elem_name, elem_attribute_name):
        """
        XML parsing helper function to find child element with a specific name,
        and return the value of a specified attribute.
        """
        elem = parent_elem.find(elem_name)
        if elem is not None:
            return elem.attrib[elem_attribute_name]

    def _get_multi_elem_text(self, parent_elem, elem_name, top_key, bottom_key):
        """
        XML parsing helper function to return a 2-level dict of multiple elements
        by a specified name, using top_key as the first key, and bottom_key as the second key
        """
        elements = parent_elem.findall(elem_name)
        # A 2-level dictionary of items, keyed by top_key and then bottom_key.
        result = {}
        if elements is not None:
            for elem in elements:
                if top_key in elem.attrib:
                    result[elem.attrib[top_key]] = {bottom_key: elem.attrib[bottom_key], 'TEXT': elem.text}
                else:
                    result['0'] = {bottom_key: elem.attrib[bottom_key], 'TEXT': elem.text}
        return result


class GracenoteQuery:
    """
    A utility class for creating and configuring an XML query for a
    POST request to the Gracenote service.
    """

    def __init__(self):
        self.root = xml.etree.ElementTree.Element('QUERIES')

    def add_auth(self, client_id, user_id):
        auth = xml.etree.ElementTree.SubElement(self.root, 'AUTH')
        client = xml.etree.ElementTree.SubElement(auth, 'CLIENT')
        user = xml.etree.ElementTree.SubElement(auth, 'USER')
        client.text = client_id
        user.text = user_id

    def add_query(self, cmd):
        query = xml.etree.ElementTree.SubElement(self.root, 'QUERY')
        query.attrib['CMD'] = cmd

    def add_query_mode(self, mode_string):
        query = self.root.find('QUERY')
        mode = xml.etree.ElementTree.SubElement(query, 'MODE')
        mode.text = mode_string

    def add_query_text_field(self, field_name, value):
        query = self.root.find('QUERY')
        text = xml.etree.ElementTree.SubElement(query, 'TEXT')
        text.attrib['TYPE'] = field_name
        text.text = value

    def add_query_option(self, parameter_name, value):
        query = self.root.find('QUERY')
        option = xml.etree.ElementTree.SubElement(query, 'OPTION')
        parameter = xml.etree.ElementTree.SubElement(option, 'PARAMETER')
        parameter.text = parameter_name
        value_elem = xml.etree.ElementTree.SubElement(option, 'VALUE')
        value_elem.text = value

    def add_query_gnid(self, gnid):
        query = self.root.find('QUERY')
        gnid_elem = xml.etree.ElementTree.SubElement(query, 'GN_ID')
        gnid_elem.text = gnid

    def add_query_client(self, client_id):
        query = self.root.find('QUERY')
        client = xml.etree.ElementTree.SubElement(query, 'CLIENT')
        client.text = client_id

    def to_string(self):
        return xml.etree.ElementTree.tostring(self.root)


class UserIDGenerator(object):
    """
    A user ID generator for the Gracenote service.
    Should be used only if there's something wrong with the current user ID.
    """

    def __init__(self, client_id):
        """
        Initializes the user ID generator.
        :param client_id: The Gracenote authentication key.
        :type client_id: str.
        """
        self.client_id = client_id

    def generate(self):
        """
        This function registers an application as a user of the Gracenote service.
        :return: A user ID, or None if an error occurred.
        """
        # Create XML request
        query = GracenoteQuery()
        query.add_query('REGISTER')
        query.add_query_client(self.client_id)
        query_xml = query.to_string()

        # POST query
        response = urllib2.urlopen(GracenoteAPI.get_gracenote_url(self.client_id),
                                   query_xml)
        response_xml = response.read()

        # Parse response
        user_id = None
        response_tree = xml.etree.ElementTree.fromstring(response_xml)
        response_elem = response_tree.find('RESPONSE')
        if response_elem.attrib['STATUS'] == 'OK':
            user_elem = response_elem.find('USER')
            user_id = user_elem.text

        return user_id