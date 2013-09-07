__author__ = 'Halti'

import os.path
from argparse import ArgumentParser

from organizer.amazon.client import AmazonClient


def main():
    """
    Organizes the MP3 album in the given path.
    Should be called with the album's path as an argument.
    Path must be in the format '...\<Artist Name>\<Album Name>\'
    """
    parser = ArgumentParser()
    parser.add_argument("-q", "--quiet", action="store_false", dest="verbose", default=True,
                        help="Don't print any output")
    parser.add_argument("-p", "--path", dest="path", required=True,
                        help="The album's path")
    parser.add_argument("-a", "--artist", dest="artist",
                        help="The artist's name")
    parser.add_argument("-b", "--album", dest="album",
                        help="The album's name")
    args = parser.parse_args()
    if not os.path.exists(args.path):
        raise PathException("Invalid path")

    # Get album and artist names.
    album = get_album(args.path, args.album)
    artist = get_artist(args.path, args.artist)

    # Get tracks info from Amazon.
    if args.verbose:
        print "Checking Amazon for tracks info"
    amazon_client = AmazonClient()
    amazon_client.connect()
    amazon_client.find_album(album, artist)

