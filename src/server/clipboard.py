from mimetypes import guess_type
from sys import getsizeof

from PyQt5.QtCore import QMimeData, QByteArray


class Clipboard:
    """
    This class acts as an intermediary between the core
    and the clipboard of the system.
    Internally it currently uses the QClipboard provided by
    the running QApplication.
    This clipoard needs to be provided in __init__.
    This class was introduced to provide the ability for further enhancement
    of the clipboard that might be needed further down the line.
    It will probably also be used to monitor the current state
    of the system-clipboard and notify the core of any occurring changes
    so those changes can be synced up with the remote-clipboard
    """

    # The QClipboard
    clipboard = None

    def _prepare_data(self, data):
        if type(data) is str:
            data = data.encode(encoding='utf8')
        else:
            data = bytes(data)
        return data

    def save(self, data):
        """
        Parses the data to a String (only for the current implementation)
            and saves it in the system's clipboard
        :param data: The data that will be saved in the clipboard
        """
        mime_type = data['mimetype']
        mime_data = QMimeData()

        prepared_data = self._prepare_data(data['data'])

        mime_data.setData(mime_type, prepared_data)
        mime_data.setData('text/plain', prepared_data)

        self.clipboard.clear()
        self.clipboard.setMimeData(mime_data)

    def __init__(self, clip):
        """
        :param clip: The QClipboard of the current QApplication
        """
        self.clipboard = clip
