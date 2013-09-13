__author__ = 'Halti'

import pytest
import os.path
from consts import *
from organizer.file_utils import *


TEST_PATH = os.path.join("C:\\", TEST_ARTIST, TEST_ALBUM)
TEST_INVALID_ALBUM_PATH = ""
TEST_INVALID_ARTIST_PATH = os.path.join("C:\\", TEST_ALBUM)


class TestUtils:
    """
    Tests for all utility functions.
    """

    def test_get_album_with_argument(self):
        assert get_album(TEST_PATH, TEST_ALBUM) == TEST_ALBUM

    def test_get_album_with_path(self):
        assert get_album(TEST_PATH) == TEST_ALBUM

    def test_get_album_invalid_path(self):
        with pytest.raises(PathException):
            get_album(TEST_INVALID_ALBUM_PATH)

    def test_get_artist_with_argument(self):
        assert get_artist(TEST_PATH, TEST_ARTIST) == TEST_ARTIST

    def test_get_artist_with_path(self):
        assert get_artist(TEST_PATH) == TEST_ARTIST

    def test_get_artist_invalid_path(self):
        with pytest.raises(PathException):
            get_artist(TEST_INVALID_ARTIST_PATH)