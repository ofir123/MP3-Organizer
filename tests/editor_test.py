import os
import shutil

import pytest

from mutagen.id3 import ID3

from mp3organizer.organizer import GRABBERS_LIST
from mp3organizer.editor import FilesEditor
from mp3organizer.datatypes.album import Album
from mp3organizer.datatypes.track import Track
from .test_consts import TEST_PATH, TEST_FILES_DIRECTORY, TEST_FILE_AUDIO, TEST_FILE_COVER, TEST_BASE_PATH, \
    TEST_ALBUM, TEST_ARTIST, TEST_GENRE, TEST_YEAR, TEST_TRACKS_LIST, TEST_TRACK, TEST_LYRICS_START, \
    TEST_LYRICS_START2, TEST_LYRICS_END, TEST_LYRICS_END2, TEST_LYRICS_END3


@pytest.fixture
def setup(request):
    """
    Sets up the test by creating a directory of dummy files.
    """
    if os.path.exists(TEST_PATH):
        shutil.rmtree(TEST_PATH)
    os.makedirs(TEST_PATH)
    test_files_directory = os.path.join(os.path.dirname(__file__), TEST_FILES_DIRECTORY)
    shutil.copy2(os.path.join(test_files_directory, TEST_FILE_AUDIO),
                 os.path.join(TEST_PATH, TEST_FILE_AUDIO))
    shutil.copy2(os.path.join(test_files_directory, TEST_FILE_COVER),
                 os.path.join(TEST_PATH, TEST_FILE_COVER))

    # Add finalizer to delete the test directory and its contents.
    def fin():
        shutil.rmtree(TEST_BASE_PATH)
    request.addfinalizer(fin)


@pytest.fixture
def test_editor():
    artwork_path = os.path.join(TEST_PATH, TEST_FILE_COVER)
    return FilesEditor(TEST_PATH, Album(TEST_ALBUM, TEST_ARTIST,
                                        TEST_GENRE, TEST_YEAR,
                                        artwork_path, TEST_TRACKS_LIST), GRABBERS_LIST)


@pytest.mark.usefixtures('setup', 'test_editor')
def test_exact_names(test_editor):
    # Create the test files.
    os.rename(os.path.join(TEST_PATH, TEST_FILE_AUDIO),
              os.path.join(TEST_PATH, 'foo.mp3'))
    shutil.copy2(os.path.join(TEST_PATH, 'foo.mp3'),
                 os.path.join(TEST_PATH, 'bar.mp3'))
    # Call the editor.
    test_editor.edit_tracks([Track(1, 'foo'), Track(2, 'bar')])
    # Check the results.
    test_files = os.listdir(TEST_PATH)
    assert len(test_files) == 3
    assert '01 - Foo.mp3' in test_files
    assert '02 - Bar.mp3' in test_files


@pytest.mark.usefixtures('setup', 'test_editor')
def test_id3_tag(test_editor):
    # Create the test file.
    os.rename(os.path.join(TEST_PATH, TEST_FILE_AUDIO),
              os.path.join(TEST_PATH, 'Yellow.mp3'))
    results = test_editor.edit_track(TEST_TRACK)
    assert results.success
    assert results.lyrics
    assert results.rename
    test_file = ID3(os.path.join(TEST_PATH, str(TEST_TRACK) + '.mp3'))
    track_number = test_file.getall('TRCK')
    assert len(track_number) == 1
    assert track_number[0].text[0] == TEST_TRACK.number
    title = test_file.getall('TIT2')
    assert len(title) == 1
    assert title[0].text[0] == TEST_TRACK.title
    artist = test_file.getall('TPE1')
    assert len(artist) == 1
    assert artist[0].text[0] == TEST_ARTIST
    album_artist = test_file.getall('TPE2')
    assert len(album_artist) == 1
    assert album_artist[0].text[0] == TEST_ARTIST
    album = test_file.getall('TALB')
    assert len(album) == 1
    assert album[0].text[0] == TEST_ALBUM
    genre = test_file.getall('TCON')
    assert len(genre) == 1
    assert genre[0].text[0] == TEST_GENRE
    year = test_file.getall('TDRC')
    assert len(year) == 1
    assert year[0].text[0].text == str(TEST_YEAR)
    artwork = test_file.getall('APIC')
    assert len(artwork) == 1
    lyrics = test_file.getall('USLT')
    assert len(lyrics) == 1
    assert lyrics[0].text.lower().startswith(TEST_LYRICS_START) or \
        lyrics[0].text.lower().startswith(TEST_LYRICS_START2)
    assert lyrics[0].text.lower().endswith(TEST_LYRICS_END) or lyrics[0].text.lower().endswith(TEST_LYRICS_END2) or \
        lyrics[0].text.lower().endswith(TEST_LYRICS_END3)
