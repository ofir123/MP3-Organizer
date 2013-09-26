__author__ = 'Halti'

import glob
import os.path
import eyeD3


class FilesEditor(object):
    """
    Holds the album's tracks actual files and edits them.
    """

    def __init__(self, path, album_data):
        """
        Initializes the editor with the files' path.
        :param path: The MP3 files' path.
        :type path: str.
        :param album_data: The album's data object.
        :type album_data: album.
        """
        self.files = glob.glob(os.path.join(path, "*.mp3"))
        self.album_data = album_data

    def edit_track(self, track):
        """
        Edits a single track, according to the given track info.
        Changes the file's name, and the following ID3 tag fields:
        Title, Track Number, Artist, Album Artist, Album, Genre, Year and Artwork.
        Also empties the following fields: Grouping, Composer and Comments.
        :param track: The track's info (number and title).
        :type track: tuple.
        """
        pass

    def edit_tracks(self, tracks_list):
        """
        Edits multiple files, according to the given tracks list.
        :param tracks_list: The tracks to edit.
        :type tracks_list: list.
        """
        for track in tracks_list:
            self.edit_track(track)
