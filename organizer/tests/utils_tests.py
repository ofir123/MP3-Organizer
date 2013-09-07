__author__ = 'Halti'


class TestUtils:
    """
    Tests for all utils.
    """

    def test_get_album(self, client):
        with pytest.raises(ConnectionException):
            client.find_album("test", prompt=False)

    def test_get_artist(self, client):
        client.connect()
        with pytest.raises(NotFoundException):
            client.find_album("asdfasdfsdflsdjaflas", prompt=False)