__author__ = 'Halti'

import pytest
import time
from consts import *
from mp3_organizer.clients.amazon_client import *


@pytest.fixture
def test_client():
    # Wait so the service won't be overflowed with requests.
    time.sleep(1)
    return AmazonClient()


@pytest.mark.usefixtures("test_client")
class TestAmazon:
    """
    Tests for the Amazon client.
    """
    def test_no_connection(self, test_client):
        with pytest.raises(ConnectionException):
            test_client.find_album(TEST_ALBUM, prompt=False, web=False)

    def test_not_found(self, test_client):
        test_client.connect()
        album = test_client.find_album(TEST_INVALID_ALBUM, prompt=False, web=False)
        assert not album

    def test_album_only(self, test_client):
        test_client.connect()
        album = test_client.find_album(TEST_ALBUM, prompt=False, web=False)
        assert album.tracks_list == TEST_TRACKS_LIST

    def test_album_and_artist(self, test_client):
        test_client.connect()
        album = test_client.find_album(TEST_ALBUM, TEST_ARTIST, prompt=False, web=False)
        assert album.tracks_list == TEST_TRACKS_LIST

