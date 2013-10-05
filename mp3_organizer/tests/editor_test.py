__author__ = 'Halti'

import pytest
import os
import glob
import shutil
from mutagen.id3 import ID3
from mp3_organizer.editor import FilesEditor
from mp3_organizer.types.album import Album
from mp3_organizer.types.track import Track
from test_consts import *


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
        shutil.rmtree(TEST_PATH)
    request.addfinalizer(fin)


@pytest.fixture
def test_editor():
    artwork_path = os.path.join(TEST_PATH, TEST_FILE_COVER)
    return FilesEditor(TEST_PATH, Album(TEST_ALBUM, TEST_ARTIST,
                                        TEST_GENRE, TEST_YEAR,
                                        artwork_path, TEST_TRACKS_LIST))


@pytest.mark.usefixtures("setup", "test_editor")
class TestEditor:
    """
    Tests for the file editor.
    """
    def test_exact_names(self, test_editor):
        # Create the test files.
        os.rename(os.path.join(TEST_PATH, TEST_FILE_AUDIO),
                  os.path.join(TEST_PATH, "foo.mp3"))
        shutil.copy2(os.path.join(TEST_PATH, "foo.mp3"),
                     os.path.join(TEST_PATH, "bar.mp3"))
        # Call the editor.
        test_editor.edit_tracks([Track(1, "foo"), Track(2, "bar")])
        # Check the results.
        test_files = glob.glob(os.path.join(TEST_PATH, "*.*"))
        assert len(test_files) == 3
        assert os.path.join(TEST_PATH, "01 - Foo.mp3") in test_files
        assert os.path.join(TEST_PATH, "02 - Bar.mp3") in test_files

    def test_exact_numbers(self, test_editor):
        # Create the test files.
        os.rename(os.path.join(TEST_PATH, TEST_FILE_AUDIO),
                  os.path.join(TEST_PATH, "01.mp3"))
        shutil.copy2(os.path.join(TEST_PATH, "01.mp3"),
                     os.path.join(TEST_PATH, "02.mp3"))
        # Call the editor.
        test_editor.edit_tracks([Track(1, "foo"), Track(2, "bar")])
        # Check the results.
        test_files = glob.glob(os.path.join(TEST_PATH, "*.*"))
        assert len(test_files) == 3
        assert os.path.join(TEST_PATH, "01 - Foo.mp3") in test_files
        assert os.path.join(TEST_PATH, "02 - Bar.mp3") in test_files

    def test_id3_tag(self, test_editor):
        assert test_editor.edit_track(
            Track(1, os.path.splitext(TEST_FILE_AUDIO)[0]), rename=False)
        test_file = ID3(os.path.join(TEST_PATH, TEST_FILE_AUDIO))
        track_number = test_file.getall("TRCK")
        assert len(track_number) == 1
        assert track_number[0].text[0] == "01"
        title = test_file.getall("TIT2")
        assert len(title) == 1
        assert title[0].text[0] == os.path.splitext(TEST_FILE_AUDIO)[0]
        artist = test_file.getall("TPE1")
        assert len(artist) == 1
        assert artist[0].text[0] == TEST_ARTIST
        album_artist = test_file.getall("TPE2")
        assert len(album_artist) == 1
        assert album_artist[0].text[0] == TEST_ARTIST
        album = test_file.getall("TALB")
        assert len(album) == 1
        assert album[0].text[0] == TEST_ALBUM
        genre = test_file.getall("TCON")
        assert len(genre) == 1
        assert genre[0].text[0] == TEST_GENRE
        year = test_file.getall("TDRC")
        assert len(year) == 1
        assert year[0].text[0].text == str(TEST_YEAR)
        artwork = test_file.getall("APIC")
        assert len(artwork) == 1