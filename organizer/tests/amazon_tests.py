__author__ = 'Halti'

import pytest
import time
from organizer.amazon.client import *


@pytest.fixture
def client():
    # Wait so the service won't be overflowed with requests.
    time.sleep(0.2)
    return AmazonClient()


@pytest.mark.usefixtures("client")
class TestAmazon:
    """
    Tests for the Amazon client.
    """

    def test_no_connection(self, client):
        with pytest.raises(ConnectionException):
            client.find_album("test", prompt=False)

    def test_not_found(self, client):
        client.connect()
        with pytest.raises(NotFoundException):
            client.find_album("asdfasdfsdflsdjaflas", prompt=False)

    def test_album_only(self, client):
        client.connect()
        track_list = client.find_album("parachutes", prompt=False)
        assert track_list == ["Don't Panic", "Shiver", "Spies",
                              "Sparks", "Yellow", "Trouble",
                              "Parachutes", "High Speed", "We Never Change",
                              "Everything's Not Lost"]

    def test_album_and_artist(self, client):
        client.connect()
        track_list = client.find_album("parachutes", "coldplay", prompt=False)
        assert track_list == ["Don't Panic", "Shiver", "Spies",
                              "Sparks", "Yellow", "Trouble",
                              "Parachutes", "High Speed", "We Never Change",
                              "Everything's Not Lost"]

