__author__ = 'Halti'

import pytest
import time
from consts import *
from organizer.client.client import *


@pytest.fixture
def client():
    # Wait so the service won't be overflowed with requests.
    time.sleep(1)
    return AmazonClient()


@pytest.mark.usefixtures("client")
class TestAmazon:
    """
    Tests for the Amazon client.
    """
    def test_no_connection(self, client):
        with pytest.raises(ConnectionException):
            client.find_album(TEST_ALBUM, prompt=False)

    def test_not_found(self, client):
        client.connect()
        tracks_list = client.find_album(TEST_INVALID_ALBUM, prompt=False)
        assert not tracks_list

    def test_album_only(self, client):
        client.connect()
        tracks_list = client.find_album(TEST_ALBUM, prompt=False)
        assert tracks_list == TEST_TRACKS_LIST

    def test_album_and_artist(self, client):
        client.connect()
        tracks_list = client.find_album(TEST_ALBUM, TEST_ARTIST, prompt=False)
        assert tracks_list == TEST_TRACKS_LIST

