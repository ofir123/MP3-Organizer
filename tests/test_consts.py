import os

from mp3organizer.datatypes.track import Track

TEST_TRACK = Track(1, 'Don\'t Panic')
TEST_ALBUM = 'Parachutes'
TEST_ARTIST = 'Coldplay'
TEST_GENRE = 'Rock'
TEST_YEAR = 2000
TEST_TRACKS_LIST = [
    Track(1, 'Don\'t Panic'),
    Track(2, 'Shiver'),
    Track(3, 'Spies'),
    Track(4, 'Sparks'),
    Track(5, 'Yellow'),
    Track(6, 'Trouble'),
    Track(7, 'Parachutes'),
    Track(8, 'High Speed'),
    Track(9, 'We Never Change'),
    Track(10, 'Everything\'s Not Lost')
]
TEST_INVALID_TITLE = 'asdfasdfsdflsdjaflas'
TEST_BASE_PATH = 'C:\\MP3_TESTS\\'
TEST_PATH = os.path.join(TEST_BASE_PATH, TEST_ARTIST, TEST_ALBUM)
TEST_LYRICS_START = 'bones sinking like stones'
TEST_LYRICS_START2 = 'bones, sinking like stones,'
TEST_LYRICS_END = 'got somebody to lean on'

# Test files constants.
TEST_FILES_DIRECTORY = 'test_files'
TEST_FILE_AUDIO = 'Audio.mp3'
TEST_FILE_COVER = 'Cover.jpg'
