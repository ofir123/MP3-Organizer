__author__ = 'Halti'

import glob
import os.path
from mutagen.id3 import ID3
from mutagen.id3 import TRCK
from mutagen.id3 import TIT2
from mutagen.id3 import TPE1
from mutagen.id3 import TPE2
from mutagen.id3 import TALB
from mutagen.id3 import TCON
from mutagen.id3 import TDRC
from mutagen.id3 import APIC


class FilesEditor(object):
    """
    Holds the album's tracks actual files and edits them.
    """

    FILES_EXTENSION = ".mp3"

    def __init__(self, path, album, verbose=True):
        """
        Initializes the editor with the files' path.
        :param path: The MP3 files' path.
        :type path: str.
        :param album: The album's data.
        :type album: album.
        :param verbose: Whether or not to print output.
        :type verbose: bool.
        """
        self.album = album
        self.verbose = verbose
        # Get all file names and normalize them.
        self.files = [x.lower().strip() for x in
                      glob.glob(os.path.join(path, "*" + FilesEditor.FILES_EXTENSION))]

    def _find_track(self, track):
        """
        Finds the given track by name, or by number.
        :param track: The track to find.
        :type track: track.
        :return: The track's file name, or None if not found.
        """
        # Try and find the track's name.
        for filename in self.files:
            if track.title.lower() in filename:
                if self.verbose:
                    print "Found track by its name."
                return filename
        # Try and find the track's number.
        for filename in self.files:
            if track.number in filename:
                if self.verbose:
                    print "Found track by its number."
                return filename
        if self.verbose:
            print "Track not found."
        return None

    def _get_mime_type(self, filename):
        """
        Finds out the mime type for the given image file.
        :param filename: The file to check.
        :type filename: str.
        :return: The mime string, or None if not supported.
        """
        extension = os.path.splitext(filename)[1]
        if extension == "png":
            return 'image/png'
        if extension == "jpg" or extension == "jpeg":
            return 'image/jpeg'
        return None

    def edit_track(self, track):
        """
        Edits a single track, according to the given track info.
        Changes the file's name, and the following ID3 tag fields:
        Title, Track Number, Artist, Album Artist, Album, Genre, Year and Artwork.
        Also empties the following fields: Grouping, Composer and Comments.
        :param track: The track's data object.
        :type track: track.
        :return: True if edited, False if not found.
        """
        if self.verbose:
            print "Looking for track: " + str(track)
        filename = self._find_track(track)
        if not filename:
            return False
        # Rename and add ID3 info.
        new_name = os.path.join(os.path.dirname(filename), str(track),
                                FilesEditor.FILES_EXTENSION)
        os.rename(filename, new_name)
        tag = ID3(new_name)
        tag.add(TRCK(encoding=3, text=track.number))
        tag.add(TIT2(encoding=3, text=track.title))
        tag.add(TPE1(encoding=3, text=self.album.artist))
        tag.add(TPE2(encoding=3, text=track.artist))
        tag.add(TALB(encoding=3, text=self.album.name))
        tag.add(TCON(encoding=3, text=self.album.genre))
        tag.add(TDRC(encoding=3, text=str(self.album.year)))
        tag.delall('APIC')
        if self.album.artwork_path:
            mime_type = self._get_mime_type(self.album.artwork_path)
            if mime_type:
                artwork_file = open(self.album.artwork_path, 'rb')
                tag.add(APIC(encoding=3, mime=mime_type, type=3,
                             desc=u'Cover', data=artwork_file.read()))
                artwork_file.close()
            elif self.verbose:
                print "Artwork file type not supported."
        # Remove unnecessary information.
        tag.delall('COMM')
        tag.delall('TCOM')
        tag.delall('TIT1')
        tag.delall('TPOS')
        tag.delall('TCMP')
        tag.save()
        return True

    def edit_tracks(self, tracks_list):
        """
        Edits multiple files, according to the given tracks list.
        :param tracks_list: The tracks to edit.
        :type tracks_list: list.
        :return: The list of failed tracks.
        """
        failed_list = []
        for track in tracks_list:
            is_success = self.edit_track(track)
            if not is_success:
                failed_list.append(track)
            elif self.verbose:
                print "Track edited successfully."
        if len(failed_list) > 0 and self.verbose:
            print "Failed tracks are: " + str(failed_list)
        return failed_list