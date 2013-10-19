from PyQt4.QtGui import QFileDialog

__author__ = 'Ofir'

import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from arguments import Arguments
from mp3_organizer.organizer import organize, CLIENTS_LIST
from mp3_organizer.file_utils import get_album, get_artist, PathException


class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class MainWindow(QtGui.QWidget):
    """
    The application's main window.
    """

    def __init__(self):
        """
        Initializes the window and its children GUI components.
        Also takes control of sys.stdout, for logging purposes.
        """
        super(MainWindow, self).__init__()
        self.dir_path_label = QtGui.QLabel("MP3 Directory:", self)
        self.album_label = QtGui.QLabel("Album title:", self)
        self.artist_label = QtGui.QLabel("Artist name:", self)
        self.genre_label = QtGui.QLabel("Genre:", self)
        self.image_path_label = QtGui.QLabel("Artwork save path:", self)
        self.client_label = QtGui.QLabel("Preferred client:", self)
        self.dir_path = QtGui.QLineEdit(self)
        self.album = QtGui.QLineEdit(self)
        self.artist = QtGui.QLineEdit(self)
        self.genre = QtGui.QLineEdit(self)
        self.image_path = QtGui.QLineEdit(self)
        self.client = QtGui.QComboBox(self)
        self.dir_button = QtGui.QPushButton("Browse...", self)
        self.start_button = QtGui.QPushButton("Start!", self)
        self.log_text = QtGui.QTextEdit(self)
        self.init_ui()

        # Install the custom output stream.
        sys.stdout = EmittingStream(textWritten=self.handle_output)

    def __del__(self):
        """
        Restores sys.stdout.
        """
        sys.stdout = sys.__stdout__

    def init_ui(self):
        """
        Initializes the UI components.
        """
        self.resize(750, 250)
        self.setWindowTitle('MP3 Organizer')
        self.setWindowIcon(QtGui.QIcon('images/music.png'))
        self._center()
        # Adjust sizes.
        self.dir_path_label.adjustSize()
        self.album_label.adjustSize()
        self.artist_label.adjustSize()
        self.genre_label.adjustSize()
        self.image_path_label.adjustSize()
        self.client_label.adjustSize()
        self.dir_button.resize(self.dir_button.sizeHint())
        self.start_button.resize(self.start_button.sizeHint())
        # Build the grid.
        grid = QtGui.QGridLayout()
        grid.setSpacing(5)
        # First row.
        grid.addWidget(self.dir_path_label, 1, 0)
        grid.addWidget(self.dir_path, 1, 1, 1, 4)
        grid.addWidget(self.dir_button, 1, 5)
        # Second row.
        grid.addWidget(self.artist_label, 2, 0)
        grid.addWidget(self.artist, 2, 1)
        grid.addWidget(self.album_label, 2, 2)
        grid.addWidget(self.album, 2, 3)
        grid.addWidget(self.genre_label, 2, 4)
        grid.addWidget(self.genre, 2, 5)
        # Third row.
        grid.addWidget(self.client_label, 3, 0)
        grid.addWidget(self.client, 3, 1)
        grid.addWidget(self.image_path_label, 3, 2)
        grid.addWidget(self.image_path, 3, 3)
        grid.addWidget(self.start_button, 3, 4, 1, 2)
        # Rest of the window.
        grid.addWidget(self.log_text, 4, 0, 5, 6)
        self.setLayout(grid)
        # Component-specific settings.
        for client in CLIENTS_LIST:
            self.client.addItem(client.get_name())
        self.dir_button.clicked.connect(self._show_dialog)
        self.start_button.clicked.connect(self._run_organizer)
        self.log_text.setReadOnly(True)
        self.start_button.setIcon(QtGui.QIcon("images/start.png"))
        self.image_path.setText("C:\\")

        self.show()

    def handle_output(self, text):
        """
        Appends text to the QTextEdit.
        :param text: The text to append.
        :type text: str.
        """
        self.log_text.append(text)

    def _center(self):
        """
        Centers the main window.
        """
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def _show_dialog(self):
        """
        Shows the directory selection dialog.
        The selected directory is then shown in the path line.
        """
        dir_name = str(QFileDialog.getExistingDirectory(self, "Select Directory", "/home"))
        try:
            album_title = get_album(dir_name)
            artist_name = get_artist(dir_name)
            self.dir_path.setText(dir_name)
            self.album.setText(album_title)
            self.artist.setText(artist_name)
        except PathException:
            QtGui.QMessageBox.critical(self, "Error",
                                       "Invalid path chosen.\nPath format is:'...\\Artist\\Album'.",
                                       QtGui.QMessageBox.Ok)
        return dir_name

    def _run_organizer(self):
        """
        Calls the MP3 organizer with the proper parameters.
        """
        print "Running organizer on path:'" + self.dir_path.text() + "'."
        args = Arguments(path=str(self.dir_path.text()), album=str(self.album.text()),
                         artist=str(self.artist.text()), genre=str(self.genre.text()),
                         image=str(self.image_path.text()), client=str(self.client.currentText()))
        organize(args)


def main():
    """
    Launches the GUI application.
    """
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()