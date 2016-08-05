import sys
import shutil
import os
import glob

import pytest
from mutagen.id3 import ID3

from mp3organizer import organizer
from .test_consts import TEST_PATH, TEST_FILES_DIRECTORY, TEST_TRACKS_LIST, TEST_FILE_AUDIO, TEST_BASE_PATH, \
    TEST_GENRE, TEST_ARTIST, TEST_ALBUM, TEST_YEAR


@pytest.fixture
def setup(request):
    """
    Sets up the system test by changing sys.argv to simulate an actual run.
    Also creates a test directory with the test album tracks inside.
    """
    if os.path.exists(TEST_PATH):
        shutil.rmtree(TEST_PATH)
    os.makedirs(TEST_PATH)
    test_files_directory = os.path.join(os.path.dirname(__file__), TEST_FILES_DIRECTORY)
    for track in TEST_TRACKS_LIST:
        shutil.copy2(os.path.join(test_files_directory, TEST_FILE_AUDIO),
                     os.path.join(TEST_PATH, '{}.mp3'.format(track.number)))

    original_argv = sys.argv
    sys.argv = [organizer.__file__]

    # Add finalizer to restore original argv and delete the test directory.
    def fin():
        sys.argv = original_argv
        shutil.rmtree(TEST_BASE_PATH)
    request.addfinalizer(fin)


@pytest.mark.usefixtures('setup')
def test_normal():
    sys.argv.extend(['--path', TEST_PATH, '--image', TEST_PATH,
                     '--genre', TEST_GENRE, '--automatic', '--no-web'])
    assert organizer.main() == []
    # Check MP3 files.
    test_mp3_files = glob.glob(os.path.join(TEST_PATH, '*.mp3'))
    assert len(test_mp3_files) == len(TEST_TRACKS_LIST)
    for mp3_file, track in zip(test_mp3_files, TEST_TRACKS_LIST):
        assert os.path.splitext(os.path.basename(mp3_file))[0] == str(track)
        mp3_info = ID3(mp3_file)
        track_number = mp3_info.getall('TRCK')
        assert len(track_number) == 1
        assert track_number[0].text[0] == track.number
        title = mp3_info.getall('TIT2')
        assert len(title) == 1
        assert title[0].text[0] == track.title
        artist = mp3_info.getall('TPE1')
        assert len(artist) == 1
        assert artist[0].text[0] == TEST_ARTIST
        album_artist = mp3_info.getall('TPE2')
        assert len(album_artist) == 1
        assert album_artist[0].text[0] == TEST_ARTIST
        album = mp3_info.getall('TALB')
        assert len(album) == 1
        assert album[0].text[0] == TEST_ALBUM
        genre = mp3_info.getall('TCON')
        assert len(genre) == 1
        assert genre[0].text[0] == TEST_GENRE
        year = mp3_info.getall('TDRC')
        assert len(year) == 1
        assert year[0].text[0].text == str(TEST_YEAR)
        artwork = mp3_info.getall('APIC')
        assert len(artwork) == 1
        lyrics = mp3_info.getall('USLT')
        assert len(lyrics) == 1
    # Check artwork file.
    artwork_files = glob.glob(os.path.join(TEST_PATH, '*.jpg'))
    assert len(artwork_files) == 1
    assert os.path.splitext(os.path.basename(artwork_files[0]))[0] == TEST_ALBUM
    # Check no other files were created.
    assert len(glob.glob(os.path.join(TEST_PATH, '*.*'))) == len(TEST_TRACKS_LIST) + 1
