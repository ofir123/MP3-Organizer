import sys
import logbook
from pathlib import Path

from PyQt5 import QtGui, QtWidgets

from mp3organizer.gui.arguments import Arguments
from mp3organizer.organizer import organize, CLIENTS_LIST, GRABBERS_LIST
from mp3organizer.file_utils import get_album, get_artist, PathException

logger = logbook.Logger('MP3OrganizerGUI')


class ConsoleLogStream(object):
    """
    A customized log handler that writes all messages to a text window.
    """
    def __init__(self, text_box):
        self.text_box = text_box

    def write(self, data):
        self.text_box.append(data)
        QtWidgets.QApplication.processEvents()


class MainWindow(QtWidgets.QWidget):
    """
    The application's main window.
    """

    def __init__(self):
        """
        Initializes the window and its children GUI components.
        Also takes control of sys.stdout, for logging purposes.
        """
        super().__init__()
        self.dir_path_label = QtWidgets.QLabel('MP3 Directory:', self)
        self.image_path_label = QtWidgets.QLabel('Artwork save path:', self)
        self.album_label = QtWidgets.QLabel('Album title:', self)
        self.artist_label = QtWidgets.QLabel('Artist name:', self)
        self.genre_label = QtWidgets.QLabel('Genre:', self)
        self.client_label = QtWidgets.QLabel('Preferred client:', self)
        self.lyrics_label = QtWidgets.QLabel('Preferred lyrics:', self)
        self.dir_path = QtWidgets.QLineEdit(self)
        self.image_path = QtWidgets.QLineEdit(self)
        self.album = QtWidgets.QLineEdit(self)
        self.artist = QtWidgets.QLineEdit(self)
        self.genre = QtWidgets.QLineEdit(self)
        self.client = QtWidgets.QComboBox(self)
        self.lyrics = QtWidgets.QComboBox(self)
        self.dir_button = QtWidgets.QPushButton('Browse...', self)
        self.image_button = QtWidgets.QPushButton('Browse...', self)
        self.start_button = QtWidgets.QPushButton('Start!', self)
        self.log_text = QtWidgets.QTextEdit(self)
        self.init_ui()

    def init_ui(self):
        """
        Initializes the UI components.
        """
        self.resize(750, 250)
        self.setWindowTitle('MP3 Organizer')
        self.setWindowIcon(QtGui.QIcon(str(Path('images') / 'music.png')))
        self._center()
        # Adjust sizes.
        self.dir_path_label.adjustSize()
        self.album_label.adjustSize()
        self.artist_label.adjustSize()
        self.genre_label.adjustSize()
        self.image_path_label.adjustSize()
        self.client_label.adjustSize()
        self.lyrics_label.adjustSize()
        self.dir_button.resize(self.dir_button.sizeHint())
        self.image_button.resize(self.image_button.sizeHint())
        self.start_button.resize(self.start_button.sizeHint())
        # Build the grid.
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(5)
        # First row.
        grid.addWidget(self.dir_path_label, 1, 0)
        grid.addWidget(self.dir_path, 1, 1, 1, 4)
        grid.addWidget(self.dir_button, 1, 5)
        # Second row.
        grid.addWidget(self.image_path_label, 2, 0)
        grid.addWidget(self.image_path, 2, 1, 1, 4)
        grid.addWidget(self.image_button, 2, 5)
        # Third row.
        grid.addWidget(self.artist_label, 3, 0)
        grid.addWidget(self.artist, 3, 1)
        grid.addWidget(self.album_label, 3, 2)
        grid.addWidget(self.album, 3, 3)
        grid.addWidget(self.genre_label, 3, 4)
        grid.addWidget(self.genre, 3, 5)
        # Fourth row.
        grid.addWidget(self.client_label, 4, 0)
        grid.addWidget(self.client, 4, 1)
        grid.addWidget(self.lyrics_label, 4, 2)
        grid.addWidget(self.lyrics, 4, 3)
        grid.addWidget(self.start_button, 4, 4, 1, 2)
        # Rest of the window.
        grid.addWidget(self.log_text, 5, 0, 5, 6)
        self.setLayout(grid)

        # Add combo boxes values.
        for client in CLIENTS_LIST:
            self.client.addItem(client.get_name())
        for grabber in GRABBERS_LIST:
            self.lyrics.addItem(grabber.get_name())
        # Connect clicks to functions.
        self.dir_button.clicked.connect(self._show_dir_dialog)
        self.image_button.clicked.connect(self._show_image_dialog)
        self.start_button.clicked.connect(self._run_organizer)
        # Set button icons.
        self.start_button.setIcon(QtGui.QIcon(str(Path('images') / 'start.png')))
        # Prepare the log window.
        self.log_text.setReadOnly(True)

        self.show()

    def handle_output(self, text):
        """
        Appends text to the QTextEdit.

        :param text: The text to append.
        """
        self.log_text.append(text)

    def _center(self):
        """
        Centers the main window.
        """
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _show_dir_dialog(self):
        """
        Shows the directory selection dialog.
        The selected directory is then shown in the path line.
        """
        dir_name = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory', '/home'))
        try:
            album_title = get_album(dir_name)
            artist_name = get_artist(dir_name)
            self.dir_path.setText(dir_name)
            self.image_path.setText(dir_name)
            self.album.setText(album_title)
            self.artist.setText(artist_name)
        except PathException:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Invalid path chosen.\nPath format is:"...\\Artist\\Album".',
                                           QtWidgets.QMessageBox.Ok)
        return dir_name

    def _show_image_dialog(self):
        """
        Shows the artwork path selection dialog.
        The selected directory is then shown in the path line.
        """
        dir_name = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory', '/home'))
        self.image_path.setText(dir_name)
        return dir_name

    def _run_organizer(self):
        """
        Calls the MP3 organizer with the proper parameters.
        """
        self.log_text.clear()
        print('Running organizer on path:"{}".'.format(self.dir_path.text()))
        args = Arguments(path=str(self.dir_path.text()), album=str(self.album.text()),
                         artist=str(self.artist.text()), genre=str(self.genre.text()),
                         image=str(self.image_path.text()), client=str(self.client.currentText()),
                         grabber=str(self.lyrics.currentText()))
        handlers_list = list()
        handlers_list.append(logbook.NullHandler())
        handlers_list.append(logbook.StreamHandler(sys.stdout, level='DEBUG', bubble=True))
        handlers_list.append(logbook.StreamHandler(sys.stderr, level='ERROR', bubble=True))
        handlers_list.append(logbook.StreamHandler(stream=ConsoleLogStream(self.log_text), bubble=True,
                                                   level=logbook.INFO))
        with logbook.NestedSetup(handlers_list).applicationbound():
            organize(args)


def main():
    """
    Launches the GUI application.
    """
    app = QtWidgets.QApplication(sys.argv)
    # We have to keep the window in a variable in order to prevent the GC from deleting it.
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
