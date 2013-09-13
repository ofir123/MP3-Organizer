__author__ = 'Halti'

import os.path
from argparse import ArgumentParser

from client.client import AmazonClient
from file_utils import *


def get_tracks_list(args):
    """
    Retrieves the tracks list from Amazon, using the Amazon client.
    """
    if args.verbose:
        print "Checking Amazon for tracks info."
    amazon_client = AmazonClient()
    amazon_client.connect()
    return amazon_client.find_album(args.album, args.artist,
                                    prompt=args.prompt, web=args.web)


def get_arguments():
    """
    Gets arguments from the user.
    path - The path of the album to organize.
    album - The album's name (makes the search for lyrics and info easier).
    artist - The album's artist (makes the search for lyrics and info easier).
    quiet - If true, no log messages will be displayed on the screen.
    automatic - If true, user will not be prompted to approve album correctness.
    web - If true, a new tab in the browser will pop up with the album's information.
    fake - If true, path doesn't exist and no actual files will be changed.
    """
    parser = ArgumentParser()
    parser.add_argument("-p", "--path", dest="path", required=True,
                        help="The album's path")
    parser.add_argument("-b", "--album", dest="album",
                        help="The album's name")
    parser.add_argument("-a", "--artist", dest="artist",
                        help="The artist's name")
    parser.add_argument("-q", "--quiet", action="store_false", dest="verbose", default=True,
                        help="Don't print any output")
    parser.add_argument("-t", "--automatic", action="store_false", dest="prompt", default=True,
                        help="Don't ask the user for input at certain points")
    parser.add_argument("-w", "--no-web", action="store_false", dest="web", default=True,
                        help="Don't open a new browser tab with the album's information")
    parser.add_argument("-f", "--fake", action="store_true", dest="fake", default=False,
                        help="Fake path for testing purposes")
    args = parser.parse_args()

    # Validate and fix arguments.
    if not args.fake and not os.path.exists(args.path):
        raise PathException("Invalid path")
    if args.path.endswith(os.path.sep):
        args.path = os.path.dirname(args.path)
    args.album = get_album(args.path, args.album)
    args.artist = get_artist(args.path, args.artist)

    return args


def main():
    """
    Organizes the MP3 album in the given path.
    Should be called with the album's path as an argument.
    Path must be in the format '...\<Artist Name>\<Album Name>'
    """
    # Get arguments from the user.
    args = get_arguments()

    # Get tracks list from Amazon.
    tracks_list = get_tracks_list(args)
    if not tracks_list:
        if args.verbose:
            print "No album was found. Exiting..."
        return

    # For test - REMOVE!
    if args.verbose:
        print tracks_list
    return tracks_list

if __name__ == "__main__":
    main()