__author__ = 'Halti'

import pytest
import os
import glob
import shutil
from mp3_organizer.editor import FilesEditor
from mp3_organizer.types.album import Album
from mp3_organizer.types.track import Track
from test_consts import TEST_ALBUM, TEST_ARTIST

TEST_DIRECTORY = "C:\\MP3_TESTS\\"
TEST_FILES_DIRECTORY = "test_files"


@pytest.fixture
def setup(request):
    """
    Sets up the test by creating a directory of dummy files.
    """
    if os.path.exists(TEST_DIRECTORY):
        shutil.rmtree(TEST_DIRECTORY)
    os.mkdir(TEST_DIRECTORY)
    test_files_directory = os.path.join(os.path.dirname(__file__), TEST_FILES_DIRECTORY)
    shutil.copy2(os.path.join(test_files_directory, "Audio.mp3"),
                 os.path.join(TEST_DIRECTORY, "Audio.mp3"))
    shutil.copy2(os.path.join(test_files_directory, "Cover.jpg"),
                 os.path.join(TEST_DIRECTORY, "Cover.jpg"))

    # Add finalizer to delete the test directory and its contents.
    def fin():
        shutil.rmtree(TEST_DIRECTORY)
    request.addfinalizer(fin)


@pytest.fixture
def test_editor():
    return FilesEditor(TEST_DIRECTORY, Album(TEST_ALBUM, TEST_ARTIST))


@pytest.mark.usefixtures("setup", "test_editor")
class TestEditor:
    """
    Tests for the file editor.
    """
    def test_exact_names(self, test_editor):
        # Create the test files.
        os.remove(os.path.join(TEST_DIRECTORY, "Cover.jpg"))
        os.rename(os.path.join(TEST_DIRECTORY, "Audio.mp3"),
                  os.path.join(TEST_DIRECTORY, "foo.mp3"))
        shutil.copy2(os.path.join(TEST_DIRECTORY, "foo.mp3"),
                     os.path.join(TEST_DIRECTORY, "bar.mp3"))
        # Call the editor.
        test_editor.edit_tracks([Track(1, "foo"), Track(2, "bar")])
        # Check the results.
        test_files = glob.glob(os.path.join(TEST_DIRECTORY, "*.*"))
        assert len(test_files) == 2
        assert "01 - Foo.mp3" in test_files
        assert "02 - Bar.mp3" in test_files

    def test_exact_numbers(self, test_editor):
        # Create the test files.
        os.remove(os.path.join(TEST_DIRECTORY, "Cover.jpg"))
        shutil.copy2(os.path.join(TEST_DIRECTORY, "foo.mp3"),
                     os.path.join(TEST_DIRECTORY, "bar.mp3"))
        os.rename(os.path.join(TEST_DIRECTORY, "Audio.mp3"),
                  os.path.join(TEST_DIRECTORY, "01.mp3"))
        shutil.copy2(os.path.join(TEST_DIRECTORY, "01.mp3"),
                     os.path.join(TEST_DIRECTORY, "02.mp3"))
        # Call the editor.
        test_editor.edit_tracks([Track(1, "foo"), Track(2, "bar")])
        # Check the results.
        test_files = glob.glob(os.path.join(TEST_DIRECTORY, "*.*"))
        assert len(test_files) == 2
        assert "01 - Foo.mp3" in test_files
        assert "02 - Bar.mp3" in test_files

