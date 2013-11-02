__author__ = 'Halti'

import pytest
from test_consts import *
from mp3_organizer.lyrics.azlyrics_grabber import *
from mp3_organizer.lyrics.lyricscom_grabber import *
from mp3_organizer.lyrics.lyricswiki_grabber import *


def azlyrics_test_grabber():
    return AZLyricsGrabber()


def lyricscom_test_grabber():
    return LyricscomGrabber()


def lyricswiki_test_grabber():
    return LyricswikiGrabber()


@pytest.mark.parametrize("test_grabber", [lyricscom_test_grabber(), lyricswiki_test_grabber()])
class TestClient:
    """
    Tests for all lyrics grabbers.
    """

    def test_not_found(self, test_grabber):
        lyrics = test_grabber.find_lyrics(TEST_INVALID_TITLE, TEST_INVALID_TITLE,
                                          prompt=False, web=False)
        assert not lyrics

    def test_track_and_artist(self, test_grabber):
        lyrics = test_grabber.find_lyrics(TEST_TRACK.title, artist=TEST_ARTIST,
                                          prompt=False, web=False)
        assert lyrics.lower().startswith(TEST_LYRICS_START) or \
               lyrics.lower().startswith(TEST_LYRICS_START2)
        assert lyrics.lower().endswith(TEST_LYRICS_END)