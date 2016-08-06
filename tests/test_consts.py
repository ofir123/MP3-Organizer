import os

from mp3organizer.datatypes.track import Track

TEST_TRACK = Track(5, 'Yellow')
TEST_ALBUM = 'Parachutes'
TEST_ARTIST = 'Coldplay'
TEST_GENRE = 'Rock'
TEST_YEAR = 2001
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
    Track(10, 'Everything\'s Not Lost (includes Hidden Track \'life Is For Living\')')
]
TEST_INVALID_TITLE = 'asdfasdfsdflsdjaflas'
TEST_BASE_PATH = 'C:\\Temp\\MP3_TESTS\\'
TEST_PATH = os.path.join(TEST_BASE_PATH, TEST_ARTIST, TEST_ALBUM)
TEST_LYRICS_START = 'look at the stars'
TEST_LYRICS_START2 = 'your skin, your skin'
TEST_LYRICS_END = '---'
TEST_LYRICS_END2 = 'and all the things that you do'
TEST_LYRICS_END3 = 'and all the things that you do.'

# Test files constants.
TEST_FILES_DIRECTORY = 'test_files'
TEST_FILE_AUDIO = 'Audio.mp3'
TEST_FILE_COVER = 'Cover.jpg'
