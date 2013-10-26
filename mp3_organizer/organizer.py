__author__ = 'Halti'

import logging
# Create logger.
LOGGER_NAME = "organizer_logger"
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG)
# Create console handler and set level to debug.
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
# Create formatter.
formatter = logging.Formatter('%(levelname)s - %(message)s')
# Add formatter to console handler.
console_handler.setFormatter(formatter)
# add ch to logger
logger.addHandler(console_handler)

import os.path
import glob
from argparse import ArgumentParser
from clients.amazon.amazon_client import AmazonClient
from clients.gracenote.gracenote_client import GracenoteClient
from mp3_organizer.lyrics.lyricscom_grabber import LyricscomGrabber
from mp3_organizer.lyrics.lyricswiki_grabber import LyricswikiGrabber
from file_utils import *
from editor import FilesEditor

# The ordered clients list.
CLIENTS_LIST = [AmazonClient, GracenoteClient]
# The ordered grabbers list.
GRABBERS_LIST = [LyricscomGrabber, LyricswikiGrabber]


class OrganizerException(Exception):
    """
    Base Class for Organizer Exceptions.
    """
    pass


def organize(args):
    """
    Start working on with the given parameters, after validating them.
    :param args: The parsed user parameters.
    :type args: args.
    :return: The failed tracks list (empty if succeeded).
    """
    # Validate and fix arguments.
    if args.client and not args.client.lower() in\
            [c.get_name().lower() for c in CLIENTS_LIST]:
        raise OrganizerException("Invalid client")
    if args.grabber and not args.grabber.lower() in\
            [g.get_name().lower() for g in GRABBERS_LIST]:
        raise OrganizerException("Invalid lyrics website")
    if not args.path or not os.path.exists(args.path):
        raise PathException("Invalid path")
    if args.image_path and not os.path.exists(args.image_path):
        raise PathException("Invalid images path")
    if args.path.endswith(os.path.sep):
        args.path = os.path.dirname(args.path)
    args.album = get_album(args.path, args.album)
    args.artist = get_artist(args.path, args.artist)
    # Get tracks list from client.
    album = get_album_data(args)
    if not album:
        if args.verbose:
            logger.info("No album was found. Exiting...")
        return
    # Edit the files.
    failed_list = edit_files(args, album)
    if len(failed_list) > 0 and args.verbose:
        logger.info("Failed tracks are: " + str(failed_list))
    if args.verbose:
        logger.info("Finished!")
    return failed_list


def edit_files(args, album):
    """
    Edits all the files according to the album data.
    :param args: The running parameters.
    :type args: args.
    :param album: The album data, received earlier from the client.
    :type album: album.
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
        logger.debug("Checking for missed files...")
    mp3_files = glob.glob(os.path.join(args.path, "*.mp3"))
    tracks = map(str, album.tracks_list)
    for mp3_file in mp3_files:
        mp3_name = os.path.splitext(os.path.basename(mp3_file))[0]
        if mp3_name not in tracks:
            failed_list.append(mp3_name)
            if args.verbose:
                logger.info("File '" + mp3_file + "' was not edited.")
    return failed_list


def get_album_data(args):
    """
    Retrieves the album data using the available clients.
    Will try each client by their order until succeeded.
    :param args: The running parameters.
    :type args: args.
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
            logger.debug("Checking " + str(client) + " for album data.")
        try:
            client.connect()
            result = client.find_album(args.album, args.artist,
                                       prompt=args.prompt, web=args.web)
            if result:
                # Add genre received from user and return the album data.
                if args.genre:
                    result.genre = args.genre
                return result
        except Exception, e:
            if args.verbose:
                logger.debug(e)
                logger.info("Failed when using " + str(client) + ".")
        if args.verbose:
            logger.debug("Proceeding to next client.")


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
    parser = ArgumentParser(description="Organize an MP3 files directory")
    required_group = parser.add_mutually_exclusive_group(required=True)
    required_group.add_argument("-p", "--path", dest="path", help="The album's path")
    required_group.add_argument("-cm", "--clients-menu", action="store_true", dest="clients_menu",
                                default=False, help="The available clients menu")
    required_group.add_argument("-lm", "--lyrics-menu", action="store_true", dest="lyrics_menu",
                                default=False, help="The available lyrics menu")
    parser.add_argument("-b", "--album", dest="album",
                        help="The album's name")
    parser.add_argument("-a", "--artist", dest="artist",
                        help="The artist's name")
    parser.add_argument("-g", "--genre", dest="genre",
                        help="The album's genre")
    parser.add_argument("-i", "--image", dest="image_path",
                        help="The path to save album artwork")
    parser.add_argument("-c", "--client", dest="client",
                        help="The client to use. Run with --clients-menu to see all possibilities.")
    parser.add_argument("-l", "--lyrics", dest="grabber",
                        help="The lyrics website to use. Run with --lyrics-menu to see all possibilities.")
    parser.add_argument("-q", "--quiet", action="store_false", dest="verbose", default=True,
                        help="Don't print any output")
    parser.add_argument("-t", "--automatic", action="store_false", dest="prompt", default=True,
                        help="Don't ask the user for input at certain points")
    parser.add_argument("-w", "--no-web", action="store_false", dest="web", default=True,
                        help="Don't open a new browser tab with the album's information")
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
        logger.info("Available clients are (sorted by order of quality):")
        for client_class in CLIENTS_LIST:
            logger.info(client_class.get_name())
        logger.info("Please run the program again with your choice, "
                    "or without one to use default order.")
        return
    # Print the lyrics menu, if asked by the user.
    if args.lyrics_menu:
        logger.info("Available lyrics websites are (sorted by order of quality):")
        for grabber_class in GRABBERS_LIST:
            logger.info(grabber_class.get_name())
        logger.info("Please run the program again with your choice, "
                    "or without one to use default order.")
        return

    return organize(args)

if __name__ == "__main__":
    main()