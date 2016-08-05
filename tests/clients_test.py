import time

import pytest

from mp3organizer.clients.amazon.amazon_client import AmazonClient
from mp3organizer.clients.gracenote.gracenote_client import GracenoteClient, ConnectionException

from .test_consts import TEST_ALBUM, TEST_INVALID_TITLE, TEST_TRACKS_LIST, TEST_ARTIST


def gracenote_test_client():
    return GracenoteClient()


def amazon_test_client():
    # Wait so the service won't be overflowed with requests.
    time.sleep(1)
    return AmazonClient()


@pytest.mark.parametrize('test_client', [gracenote_test_client(), amazon_test_client()])
def test_no_connection(test_client):
    with pytest.raises(ConnectionException):
        test_client.find_album(TEST_ALBUM, prompt=False, web=False)


@pytest.mark.parametrize('test_client', [gracenote_test_client(), amazon_test_client()])
def test_not_found(test_client):
    test_client.connect()
    album = test_client.find_album(TEST_INVALID_TITLE, prompt=False, web=False)
    assert not album


@pytest.mark.parametrize('test_client', [gracenote_test_client(), amazon_test_client()])
def test_album_only(test_client):
    test_client.connect()
    album = test_client.find_album(TEST_ALBUM, prompt=False, web=False)
    assert album.tracks_list == TEST_TRACKS_LIST


@pytest.mark.parametrize('test_client', [gracenote_test_client(), amazon_test_client()])
def test_album_and_artist(test_client):
    test_client.connect()
    album = test_client.find_album(TEST_ALBUM, TEST_ARTIST, prompt=False, web=False)
    assert album.tracks_list == TEST_TRACKS_LIST
