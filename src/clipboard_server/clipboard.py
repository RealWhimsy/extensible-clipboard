from json import dumps
import re

from PyQt5.QtCore import pyqtSignal, QMimeData, QObject


class Clipboard(QObject):
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
    clipboard_changed_signal = pyqtSignal(list)

    def _prepare_data(self, data):
        if type(data) is str:
            data = data.encode(encoding='utf8')
        elif type(data) is dict:
            data = dumps(data)
            data = data.encode(encoding='utf8')
        else:
            data = bytes(data)
        return data

    def _string_from_qByteArray(self, array):
        return bytes.decode(array.data())

    def _is_mime_type(self, mime_string):
        return self.mime_pattern.match(mime_string)

    def save(self, data):
        """
        Parses the data to a String (only for the current implementation)
            and saves it in the system's clipboard
        :param data: The data that will be saved in the clipboard
        """
        mime_type = data['mimetype']
        self.mime_data = QMimeData()

        prepared_data = self._prepare_data(data['data'])

        self.mime_data.setData(mime_type, prepared_data)

        self.clipboard.clear()
        self.clipboard.setMimeData(self.mime_data)

        if data.get('parent'):  # If child gotten first, should not happen
            self.current_id = data['parent']
        else:
            self.current_id = data['_id']

    def update(self, data):
        # Refresh object b/c it gets deleted sometimes
        print(data['mimetype'])
        """
        self.mime_data = self.clipboard.mimeData()
        mime_type = data['mimetype']
        prepared_data = self._prepare_data(data['data'])
        self.mime_data.setData(mime_type, prepared_data)
        self.clipboard.setMimeData(self.mime_data)
        """

    def onDataChanged(self):
        # if change was triggerd by inserting data received from server
        if self.clipboard.ownsClipboard():
            return
        mime_data = self.clipboard.mimeData()
        data = []
        for dt in mime_data.formats():
            if self._is_mime_type(dt) and ';charset=' not in dt:
                try:
                    clip_data = self._string_from_qByteArray(
                            mime_data.data(dt))
                except UnicodeDecodeError:
                    clip_data = mime_data.data(dt).data()
                if clip_data:
                    # Different images formats are often empty, maybe some
                    # implicit conversion on OS-level is supposed to provide
                    data.append({
                        'mimetype': dt,
                        'data': clip_data
                    })
        self.clipboard_changed_signal.emit(data)

    def __init__(self, clip, sync_clipboard):
        """
        :param clip: The QClipboard of the current QApplication
        """
        super(QObject, self).__init__()
        self.clipboard = clip
        self.current_id = ''
        self.mime_data = QMimeData()
        # https://tools.ietf.org/html/rfc6838#section-4.2
        self.mime_pattern = re.compile(
                '^([a-zA-Z1-9][a-zA-Z1-9!#$&-^.+]{0,126})'
                + '/'
                + '([a-zA-Z1-9][a-zA-Z1-9!#$&-^.+]{0,126})$')
        if sync_clipboard:
            self.clipboard.dataChanged.connect(self.onDataChanged)
