import pytest

from mp3organizer.lyrics.azlyrics_grabber import AZLyricsGrabber
from mp3organizer.lyrics.lyricscom_grabber import LyricscomGrabber
from mp3organizer.lyrics.lyricswiki_grabber import LyricswikiGrabber
from mp3organizer.lyrics.songlyrics_grabber import SongLyricsGrabber
from tests.test_consts import TEST_ARTIST, TEST_INVALID_TITLE, TEST_LYRICS_END, TEST_LYRICS_START2, TEST_LYRICS_START, \
    TEST_TRACK


def azlyrics_test_grabber():
    return AZLyricsGrabber()


def lyricscom_test_grabber():
    return LyricscomGrabber()


def lyricswiki_test_grabber():
    return LyricswikiGrabber()


def songlyrics_test_grabber():
    return SongLyricsGrabber()


@pytest.mark.parametrize('test_grabber', [lyricscom_test_grabber(), lyricswiki_test_grabber()])
def test_not_found(test_grabber):
    lyrics = test_grabber.find_lyrics(TEST_INVALID_TITLE, TEST_INVALID_TITLE)
    assert not lyrics


@pytest.mark.parametrize('test_grabber', [lyricscom_test_grabber(), lyricswiki_test_grabber()])
def test_track_and_artist(test_grabber):
    lyrics = test_grabber.find_lyrics(TEST_TRACK.title, artist=TEST_ARTIST)
    assert lyrics.lower().startswith(TEST_LYRICS_START) or \
        lyrics.lower().startswith(TEST_LYRICS_START2)
    assert lyrics.lower().endswith(TEST_LYRICS_END)
