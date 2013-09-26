__author__ = 'Halti'

import sys
import pytest
from test_consts import *
from mp3_organizer import organizer


@pytest.fixture
def setup(request):
    """
    Sets up the system test by changing sys.argv to simulate an actual run.
    """
    original_argv = sys.argv
    sys.argv = [organizer.__file__]

    # Add finalizer to restore original argv.
    def fin():
        sys.argv = original_argv
    request.addfinalizer(fin)


@pytest.mark.usefixtures("setup")
class TestOrganizer:
    """
    System tests for the entire organizer.
    """
    def test_path(self):
        sys.argv.extend(["--path", TEST_PATH, "--fake", "--automatic", "--no-web"])
        assert organizer.main() == TEST_TRACKS_LIST

    def test_path_and_album(self):
        sys.argv.extend(["--path", TEST_PATH, "--album", TEST_ALBUM,
                         "--fake", "--automatic", "--no-web"])
        assert organizer.main() == TEST_TRACKS_LIST

    def test_path_and_artist(self):
        sys.argv.extend(["--path", TEST_PATH, "--artist", TEST_ARTIST,
                         "--fake", "--automatic", "--no-web"])
        assert organizer.main() == TEST_TRACKS_LIST

    def test_path_and_album_and_artist(self):
        sys.argv.extend(["--path", TEST_PATH, "--album", TEST_ALBUM,
                         "--artist", TEST_ARTIST, "--fake", "--automatic", "--no-web"])
        assert organizer.main() == TEST_TRACKS_LIST

