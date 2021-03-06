import glob
import os.path
import re

import logbook
from mutagen.id3 import ID3, TRCK, TIT2, TPE1, TPE2, TALB, TCON, TDRC, APIC, USLT, ID3NoHeaderError

from .file_utils import normalize_name, get_mime_type

logger = logbook.Logger('MP3OrganizerEditor')


class EditResults(object):
    """
    A simple object representing the editing process result of a file.
    """

    def __init__(self, track, success=False, lyrics=False, rename=False):
        self.track = track
        self.success = success
        self.lyrics = lyrics
        self.rename = rename

    def __repr__(self):
        string = '{}: Editing '.format(self.track)
        if not self.success:
            string += 'failed'
        else:
            string += 'succeeded'
            if self.lyrics:
                string += ' with lyrics'
            if self.rename:
                string += '. File was renamed'
        return string


class FilesEditor(object):
    """
    Holds the album's tracks actual files and edits them.
    """

    FILES_EXTENSION = '.mp3'

    def __init__(self, path, album, grabbers_list=None, prompt=True,
                 web=True, verbose=True):
        """
        Initializes the editor with the files' path.

        :param path: The MP3 files' path.
        :param album: The album's data.
        :param grabbers_list: The list of lyrics grabbers to use.
        :param prompt: Whether or not to prompt the user for approval.
        :param web: Whether or not to open a browser with the lyrics' information.
        :param verbose: Whether or not to print output.
        """
        self.path = path
        self.album = album
        self.grabbers_list = grabbers_list
        self.prompt = prompt
        self.web = web
        self.verbose = verbose

    def _find_track(self, track):
        """
        Finds the given track by name.
        When searching by name, always returns the shortest result.

        :param track: The track to find.
        :return: The track's file name, or None if not found.
        """
        # Get all file names and normalize them.
        files = glob.glob(os.path.join(self.path, '*' + FilesEditor.FILES_EXTENSION))
        # Try and find the track's name.
        optional_files = []
        for filename in files:
            if len(re.findall(r'\b' + normalize_name(track.title) + r'\b',
                              normalize_name(os.path.splitext(os.path.basename(filename))[0]))) > 0:
                optional_files.append(filename)
        if len(optional_files) > 0:
            if self.verbose:
                logger.debug('Found track by its name.')
            optional_files.sort(key=len)
            return optional_files[0]
        # No file was found.
        if self.verbose:
            logger.warning('Track not found.')
        return None

    def _get_lyrics(self, track):
        """
        Uses the grabbers list to find lyrics for the given track.

        :param track: The track to find lyrics to.
        :return: The track's lyrics, or None if not found.
        """
        for grabber_class in self.grabbers_list:
            grabber = grabber_class(verbose=self.verbose)
            if self.verbose:
                logger.info('Checking {} for lyrics.'.format(grabber))
            try:
                result = grabber.find_lyrics(track.title, artist=self.album.artist,
                                             album=self.album.name)
                if result:
                    if self.verbose:
                        logger.debug('Lyrics found!')
                    return result
            except Exception as ex:
                if self.verbose:
                    logger.debug(ex)
                    logger.warning('Error occurred when using {}.'.format(grabber))
            if self.verbose:
                logger.debug('Lyrics not found using {}. Proceeding to next grabber.'.format(grabber))

    def edit_track(self, track, rename=True, lyrics=True):
        """
        Edits a single track, according to the given track info.
        Changes the file's name, and the following ID3 tag fields:
        Title, Track Number, Artist, Album Artist, Album, Genre, Year and Artwork.
        Also empties the following fields: Grouping, Composer and Comments.

        :param track: The track's data object.
        :param rename: Whether to rename the file or not.
        :param lyrics: Whether to add lyrics or not.
        :return: edit results.
        """
        if self.verbose:
            logger.info('Looking for track: {}'.format(track))
        results = EditResults(track)
        filename = self._find_track(track)
        if not filename:
            return results
        if rename:
            new_name = os.path.join(os.path.dirname(filename),
                                    str(track)) + FilesEditor.FILES_EXTENSION
            if new_name != filename:
                os.rename(filename, new_name)
                results.rename = True
                if self.verbose:
                    logger.debug('File "{}" was renamed to "{}".'.format(filename, new_name))
        else:
            new_name = filename

        # Edit ID3 information.
        try:
            tag = ID3(new_name)
        except ID3NoHeaderError:
            tag = ID3()
        tag.add(TRCK(encoding=3, text=track.number))
        tag.add(TIT2(encoding=3, text=track.title))
        tag.add(TPE1(encoding=3, text=self.album.artist))
        tag.add(TPE2(encoding=3, text=self.album.artist))
        album_suffix = ' CD {}'.format(track.disc_num) if track.disc_num else ''
        tag.add(TALB(encoding=3, text=self.album.name + album_suffix))
        tag.add(TCON(encoding=3, text=self.album.genre))
        tag.add(TDRC(encoding=3, text=str(self.album.year)))
        # Edit the artwork.
        tag.delall('APIC')
        if self.album.artwork_path:
            mime_type = get_mime_type(self.album.artwork_path)
            if mime_type:
                artwork_file = open(self.album.artwork_path, 'rb')
                tag.add(APIC(encoding=3, mime=mime_type, type=3, desc='Cover', data=artwork_file.read()))
                artwork_file.close()
            elif self.verbose:
                logger.warning('Artwork file type not supported.')
        # Add lyrics.
        tag.delall('USLT')
        if lyrics:
            result_lyrics = self._get_lyrics(track)
            if result_lyrics:
                tag.add(USLT(encoding=3, lang='eng', desc='Lyrics', text=result_lyrics))
                results.lyrics = True
            elif self.verbose:
                logger.info('Couldn\'t find lyrics.')
        # Remove unnecessary information.
        tag.delall('COMM')
        tag.delall('TCOM')
        tag.delall('TIT1')
        tag.delall('TPOS')
        tag.delall('TCMP')
        tag.save(new_name)
        results.success = True
        return results

    def edit_tracks(self, tracks_list=None):
        """
        Edits multiple files, according to the given tracks list.

        :param tracks_list: The tracks to edit. Uses the current album's list if None.
        :return: The list of failed tracks.
        """
        failed_list = []
        success_list = []
        if not tracks_list:
            tracks_list = self.album.tracks_list
        for track in tracks_list:
            results = self.edit_track(track)
            if not results.success:
                failed_list.append(results)
                if self.verbose:
                    logger.warning('Track "{}" editing failed.'.format(track))
            else:
                success_list.append(results)
                if self.verbose:
                    logger.info('Track "{}" editing succeeded.'.format(track))
        # Log the results.
        if len(success_list) > 0 and self.verbose:
            logger.info('Successful tracks are: ')
            for result in success_list:
                logger.info(str(result) + '.')
        return failed_list
