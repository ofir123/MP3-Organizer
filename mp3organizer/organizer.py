import glob
import os
import sys
from argparse import ArgumentParser

import logbook

from mp3organizer.clients.amazon.amazon_client import AmazonClient
from mp3organizer.clients.gracenote.gracenote_client import GracenoteClient
from mp3organizer.file_utils import get_artist, get_album, PathException
from mp3organizer.lyrics.lyricscom_grabber import LyricscomGrabber
from mp3organizer.lyrics.lyricswiki_grabber import LyricswikiGrabber
from mp3organizer.lyrics.azlyrics_grabber import AZLyricsGrabber
from mp3organizer.lyrics.songlyrics_grabber import SongLyricsGrabber
from mp3organizer.editor import FilesEditor

LOG_FILE_NAME = 'mp3organizer.log'
# The ordered clients list.
CLIENTS_LIST = [AmazonClient, GracenoteClient]
# The ordered grabbers list.
GRABBERS_LIST = [AZLyricsGrabber, LyricswikiGrabber, LyricscomGrabber, SongLyricsGrabber]

logger = logbook.Logger('MP3Organizer')


def _get_log_handlers(logs_directory_path=None):
    """
    Returns a list of the nested log handlers setup.
    """
    handlers_list = list()
    handlers_list.append(logbook.NullHandler())
    # Add the rotating file handler, if a logs directory path was supplied.
    if logs_directory_path is not None:
        if not os.path.exists(logs_directory_path):
            os.makedirs(logs_directory_path)
        handlers_list.append(logbook.RotatingFileHandler(os.path.join(logs_directory_path, LOG_FILE_NAME),
                                                         max_size=1024 * 1024, backup_count=5, bubble=True))
    handlers_list.append(logbook.StreamHandler(sys.stdout, level='DEBUG', bubble=True))
    handlers_list.append(logbook.StreamHandler(sys.stderr, level='ERROR', bubble=True))
    return handlers_list


class OrganizerException(Exception):
    """
    Base Class for Organizer Exceptions.
    """
    pass


def organize(args):
    """
    Start working on with the given parameters, after validating them.

    :param args: The parsed user parameters.
    :return: The failed tracks list (empty if succeeded).
    """
    # Validate and fix arguments.
    if args.client and not args.client.lower() in \
            [c.get_name().lower() for c in CLIENTS_LIST]:
        raise OrganizerException('Invalid client')
    if args.grabber and not args.grabber.lower() in \
            [g.get_name().lower() for g in GRABBERS_LIST]:
        raise OrganizerException('Invalid lyrics website')
    if not args.path or not os.path.exists(args.path):
        raise PathException('Invalid path')
    if args.image_path and not os.path.exists(args.image_path):
        raise PathException('Invalid images path')
    if args.path.endswith(os.path.sep):
        args.path = os.path.dirname(args.path)
    args.album = get_album(args.path, args.album)
    args.artist = get_artist(args.path, args.artist)
    # Get tracks list from client.
    album = get_album_data(args)
    if not album:
        if args.verbose:
            logger.info('No album was found. Exiting...')
        return
    # Edit the files.
    failed_list = edit_files(args, album)
    if len(failed_list) > 0 and args.verbose:
        logger.info('Failed tracks are: {}'.format(failed_list))
    if args.verbose:
        logger.info('Finished!')
    return failed_list


def edit_files(args, album):
    """
    Edits all the files according to the album data.

    :param args: The running parameters.
    :param album: The album data, received earlier from the client.
    :return: The failed tracks list (empty if succeeded).
    """
    # If user supplied a specific lyrics website, put it first on the list.
    grabbers = GRABBERS_LIST
    if args.grabber:
        for index, grabber_class in enumerate(grabbers):
            if grabber_class.get_name().lower() == args.grabber.lower():
                grabber_index = index
                grabbers.insert(0, grabbers.pop(grabber_index))
                break

    editor = FilesEditor(args.path, album, grabbers, args.prompt,
                         args.web, args.verbose)
    failed_list = editor.edit_tracks()
    # Check for missed files.
    if args.verbose:
        logger.debug('Checking for missed files...')
    mp3_files = glob.glob(os.path.join(args.path, '*.mp3'))
    tracks = map(str, album.tracks_list)
    for mp3_file in mp3_files:
        mp3_name = os.path.splitext(os.path.basename(mp3_file))[0]
        if mp3_name not in tracks:
            failed_list.append(mp3_name)
            if args.verbose:
                logger.info('File "{}" was not edited.'.format(mp3_file))
    return failed_list


def get_album_data(args):
    """
    Retrieves the album data using the available clients.
    Will try each client by their order until succeeded.

    :param args: The running parameters.
    :returns: The album data.
    """
    clients = CLIENTS_LIST
    # If user supplied a specific client, put it first on the list.
    if args.client:
        for index, client_class in enumerate(clients):
            if client_class.get_name().lower() == args.client.lower():
                client_index = index
                clients.insert(0, clients.pop(client_index))
                break
    # Try every client in the list, until succeeded.
    for client_class in clients:
        client = client_class(artwork_folder=args.image_path, verbose=args.verbose)
        if args.verbose:
            logger.debug('Checking {} for album data.'.format(client))
        try:
            client.connect()
            result = client.find_album(args.album, args.artist,
                                       prompt=args.prompt, web=args.web)
            if result:
                # Add genre received from user and return the album data.
                if args.genre:
                    result.genre = args.genre
                return result
        except Exception as ex:
            if args.verbose:
                logger.debug(ex)
                logger.info('Failed when using {}.'.format(client))
        if args.verbose:
            logger.debug('Proceeding to next client.')


def get_arguments():
    """
    Gets arguments from the user.

    path - The path of the album to organize.
    clients menu - Prints the available clients menu (conflicts with path).
    lyrics menu - Prints the available lyrics website menu (conflicts with path).
    album - The album's name (makes the search for lyrics and info easier).
    artist - The album's artist (makes the search for lyrics and info easier).
    genre - The album's genre.
    image - The path to save the album's artwork.
    client - The client to use.
    lyrics - The lyrics website to use.
    quiet - If true, no log messages will be displayed on the screen.
    automatic - If true, user will not be prompted to approve album correctness.
    web - If true, a new tab in the browser will pop up with the album's information.
    """
    parser = ArgumentParser(description='Organize an MP3 files directory')
    required_group = parser.add_mutually_exclusive_group(required=True)
    required_group.add_argument('-p', '--path', dest='path', help='The album\'s path')
    required_group.add_argument('-cm', '--clients-menu', action='store_true', dest='clients_menu',
                                default=False, help='The available clients menu')
    required_group.add_argument('-lm', '--lyrics-menu', action='store_true', dest='lyrics_menu',
                                default=False, help='The available lyrics menu')
    parser.add_argument('-b', '--album', dest='album',
                        help='The album\'s name')
    parser.add_argument('-a', '--artist', dest='artist',
                        help='The artist\'s name')
    parser.add_argument('-g', '--genre', dest='genre',
                        help='The album\'s genre')
    parser.add_argument('-i', '--image', dest='image_path',
                        help='The path to save album artwork')
    parser.add_argument('-c', '--client', dest='client',
                        help='The client to use. Run with --clients-menu to see all possibilities.')
    parser.add_argument('-l', '--lyrics', dest='grabber',
                        help='The lyrics website to use. Run with --lyrics-menu to see all possibilities.')
    parser.add_argument('-q', '--quiet', action='store_false', dest='verbose', default=True,
                        help='Don\'t print any output')
    parser.add_argument('-t', '--automatic', action='store_false', dest='prompt', default=True,
                        help='Don\'t ask the user for input at certain points')
    parser.add_argument('-w', '--no-web', action='store_false', dest='web', default=True,
                        help='Don\'t open a new browser tab with the album\'s information')
    parser.add_argument('-d', '--logs-directory', dest='logs_directory',
                        help='The directory to save log files in.')
    return parser.parse_args()


def main():
    """
    Organizes the MP3 album in the given path.
    Should be called with the album's path as an argument.
    Path must be in the format '...\<Artist Name>\<Album Name>'
    """
    # Get arguments from the user.
    args = get_arguments()
    # Print the clients menu, if asked by the user.
    if args.clients_menu:
        print('Available clients are (sorted by order of quality):')
        for client_class in CLIENTS_LIST:
            print(client_class.get_name())
        print('Please run the program again with your choice, '
              'or without one to use default order.')
        return
    # Print the lyrics menu, if asked by the user.
    if args.lyrics_menu:
        print('Available lyrics websites are (sorted by order of quality):')
        for grabber_class in GRABBERS_LIST:
            print(grabber_class.get_name())
        print('Please run the program again with your choice, '
              'or without one to use default order.')
        return
    with logbook.NestedSetup(_get_log_handlers(args.logs_directory)).applicationbound():
        return organize(args)


if __name__ == '__main__':
    main()
