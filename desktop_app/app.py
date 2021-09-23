import sys
import json
import requests
from copy import deepcopy
from PyQt5 import uic, QtGui, QtCore, QtWidgets

CLIP_ID = 'clip_id'
MIME_TYPE = 'mime_type'

class ClipboardApp(QtWidgets.QMainWindow):
    """
    Main window for the clipboard app
    """

    clips = []
    filtered_clips = []

    def __init__(self, server_address, parent=None):
        super(ClipboardApp, self).__init__(parent)
        self.server_address = str(server_address)
        self._init_threads()
        self._init_clip_url()
        self._init_ui()
        self._get_all_clips()
        self._init_click_listeners()
        self._init_search_list()
        self.show()

    def _init_threads(self):
        self.get_filtered_clip_thread = None
        self.get_filtered_clip_worker = None
        self.delete_clip_thread = None
        self.delete_clip_worker = None
        self.get_all_clips_thread = None
        self.get_all_clips_worker = None

    def _init_clip_url(self):
        if not self.server_address.endswith('/'):
            self.server_address += '/'

        if 'http://' not in self.server_address and 'https://' not in self.server_address:
            self.server_address = 'http://' + self.server_address

        self.clip_url = self.server_address + 'clips/'

    def _init_ui(self):
        self.search_widget = uic.loadUi('search_form.ui')
        self.setCentralWidget(self.search_widget)
        self.setMinimumSize(700, 520)

        self.user_id_input = self.search_widget.userIdInput
        self.user_name_input = self.search_widget.userNameInput
        self.clip_id_input = self.search_widget.clipIdInput
        self.mime_type_input = self.search_widget.mimeTypeInput
        self.info_label = self.search_widget.infoLabel
        self.refresh_button = self.search_widget.refreshButton

    def _init_click_listeners(self):
        self.search_button = self.search_widget.searchButton
        self.reset_button = self.search_widget.resetButton

        self.search_button.clicked.connect(self.on_search_clicked)
        self.reset_button.clicked.connect(self.on_reset_clicked)
        self.refresh_button.clicked.connect(self.on_refresh_clicked)

    def on_search_clicked(self):
        """
        Filters the clips by the search parameters entered by the user.
        """
        user_id = self.user_id_input.text()
        user_name = self.user_name_input.text()
        clip_id = self.clip_id_input.text()
        mime_type = self.mime_type_input.text()

        self.filtered_clips = []

        for clip in self.clips:
            if user_id != '':
                if clip['user_id'] is None or user_id not in clip['user_id']:
                    continue

            if user_name != '':
                if clip['user_name'] is None or user_name not in clip['user_name']:
                    continue

            if clip_id != '':
                if clip_id not in clip['_id']:
                    continue

            if mime_type != '':
                if mime_type not in clip['mimetype']:
                    continue

            self.filtered_clips.append(clip)

        self.update_list_items()

    def on_reset_clicked(self):
        """
        On clicking the reset button:
        Clear the list.
        Clear all search parameters.
        Add items back to the list.
        """
        self.search_list.clear()
        self.clear_search_form()
        self.add_clips_to_list(self.clips)

    def on_refresh_clicked(self):
        """
        Load clips from the server again.
        """
        self._get_all_clips()


    def clear_search_form(self):
        """
        Clears all user input from the search form
        """
        self.user_id_input.setText('')
        self.user_name_input.setText('')
        self.clip_id_input.setText('')
        self.mime_type_input.setText('')

    def update_list_items(self):
        self.search_list.clear()
        self.add_clips_to_list(self.filtered_clips)

    def _get_all_clips(self):
        self.info_label.setText("Loading clips...")

        self.get_all_clips_thread = QtCore.QThread()
        self.get_all_clips_worker = GetAllClipsWorker(self.clip_url)
        self.get_all_clips_worker.moveToThread(self.get_all_clips_thread)

        self.get_all_clips_thread.started.connect(self.get_all_clips_worker.run)
        self.get_all_clips_worker.finished.connect(self.get_all_clips_thread.quit)
        self.get_all_clips_worker.finished.connect(self.get_all_clips_worker.deleteLater)
        self.get_all_clips_thread.finished.connect(self.get_all_clips_thread.deleteLater)
        self.get_all_clips_worker.received_data.connect(self.on_all_clips_received)

        self.get_all_clips_thread.start()

    def on_all_clips_received(self, response):
        self.clips = json.loads(response.text)
        self.clips.reverse()  # display newest clips on top
        self.filtered_clips = deepcopy(self.clips)
        self.on_search_clicked()
        self.info_label.setText("Ready")

    def _init_search_list(self):
        self.search_list = self.search_widget.searchListWidget
        self.add_clips_to_list(self.clips)

    def add_clips_to_list(self, clips):
        for clip in clips:
            item = ListItem()
            item.set_content(clip['_id'], clip['mimetype'], clip['creation_date'], clip['user_name'], clip['filename'])
            item.copy_signal.connect(self.on_item_copy_clicked)
            item.delete_signal.connect(self.on_item_delete_clicked)

            list_item = QtWidgets.QListWidgetItem(self.search_list)
            list_item.setSizeHint(item.sizeHint())

            self.search_list.addItem(list_item)
            self.search_list.setItemWidget(list_item, item)

    def on_item_copy_clicked(self, clip_dict):
        self.info_label.setText("Retrieving clip data... please wait!")

        self.get_filtered_clip_thread = QtCore.QThread()
        self.get_filtered_clip_worker = GetFilteredClipWorker(self.clip_url, clip_dict)
        self.get_filtered_clip_worker.moveToThread(self.get_filtered_clip_thread)

        self.get_filtered_clip_thread.started.connect(self.get_filtered_clip_worker.run)
        self.get_filtered_clip_worker.finished.connect(self.get_filtered_clip_thread.quit)
        self.get_filtered_clip_worker.finished.connect(self.get_filtered_clip_worker.deleteLater)
        self.get_filtered_clip_thread.finished.connect(self.get_filtered_clip_thread.deleteLater)
        self.get_filtered_clip_worker.received_data.connect(self.set_clipboard_data)

        self.get_filtered_clip_thread.start()

    def on_item_delete_clicked(self, clip_id):
        self.info_label.setText("Deleting... Please Wait")
        self.delete_clip_thread = QtCore.QThread()
        self.delete_clip_worker = DeleteClipWorker(self.clip_url, clip_id)
        self.delete_clip_worker.moveToThread(self.delete_clip_thread)

        self.delete_clip_thread.started.connect(self.delete_clip_worker.run)
        self.delete_clip_worker.finished.connect(self.delete_clip_thread.quit)
        self.delete_clip_worker.finished.connect(self.delete_clip_worker.deleteLater)
        self.delete_clip_thread.finished.connect(self.delete_clip_thread.deleteLater)
        self.delete_clip_worker.success.connect(lambda: self.delete_clip(clip_id))

        self.delete_clip_thread.start()

    def delete_clip(self, clip_id):
        self.clips = [clip for clip in self.clips if clip_id not in clip['_id']]
        self.filtered_clips = [clip for clip in self.filtered_clips if clip_id not in clip['_id']]

        self.update_list_items()
        self.info_label.setText("Successfully deleted clip " + clip_id + "!")

    def set_clipboard_data(self, data):
        try:
            QtWidgets.QApplication.clipboard().setMimeData(data)
            self.info_label.setText("Clip copied!")
        except Exception:
            self.info_label.setText("Something went wrong!")


class ListItem(QtWidgets.QWidget):
    """
    Custom list item used to display the clips.
    Shows general info about the clip in text labels and has buttons for
    copying and deleting a clip.
    """

    copy_signal = QtCore.pyqtSignal(dict)
    delete_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(ListItem, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QHBoxLayout()
        self.ui = uic.loadUi('list_item_ui.ui')
        self.clip_id_label = self.ui.clipIdLabel
        self.mime_type_label = self.ui.mimeTypeLabel
        self.date_label = self.ui.dateLabel
        self.user_name_label = self.ui.userNameLabel
        self.file_name_label = self.ui.fileNameLabel
        self.copy_button = self.ui.copyButton
        self.delete_button = self.ui.deleteButton

        layout.addWidget(self.ui)
        self.setLayout(layout)
        self.setup_click_listeners()

    def set_content(self, clip_id, mime_type, date, user_name, file_name):
        self.clip_id_label.setText(str(clip_id))
        self.mime_type_label.setText(str(mime_type))
        self.date_label.setText(str(date))
        self.user_name_label.setText(str(user_name))
        self.file_name_label.setText(str(file_name))

    def setup_click_listeners(self):
        self.copy_button.clicked.connect(self.on_copy_clicked)
        self.delete_button.clicked.connect(self.on_delete_clicked)

    def on_copy_clicked(self):
        clip_dict = {MIME_TYPE: self.mime_type_label.text(), CLIP_ID: self.clip_id_label.text()}
        self.copy_signal.emit(clip_dict)

    def on_delete_clicked(self):
        self.delete_signal.emit(self.clip_id_label.text())


class DeleteClipWorker(QtCore.QObject):
    """
    Worker class for running the http delete request on its own thread to prevent locking the UI
    """
    finished = QtCore.pyqtSignal()
    success = QtCore.pyqtSignal()

    def __init__(self, clip_url, clip_id):
        super(DeleteClipWorker, self).__init__()
        self.clip_url = clip_url
        self.clip_id = clip_id

    def run(self):
        r = requests.delete(self.clip_url + self.clip_id)

        if r.status_code == 200:
            self.success.emit()


class GetFilteredClipWorker(QtCore.QObject):
    """
    Worker class for running the http get request on its own thread to prevent locking the UI
    """
    finished = QtCore.pyqtSignal()
    received_data = QtCore.pyqtSignal(QtCore.QMimeData)

    def __init__(self, clip_url, clip_dict):
        super(GetFilteredClipWorker, self).__init__()
        self.clip_url = clip_url
        self.clip_dict = clip_dict

    def run(self):
        global app
        req = requests.get(self.clip_url + self.clip_dict[CLIP_ID])

        if req.status_code == 200:
            content = req.content

            data = QtCore.QMimeData()

            mime_type = self.clip_dict[MIME_TYPE]

            if 'image' in mime_type:
                data.setImageData(content)

            elif 'html' in mime_type:
                data.setHtml(content.decode())

            elif 'text' in mime_type:
                data.setText(content.decode())

            self.received_data.emit(data)


class GetAllClipsWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    received_data = QtCore.pyqtSignal(requests.Response)

    def __init__(self, clip_url):
        super(GetAllClipsWorker, self).__init__()
        self.clip_url = clip_url

    def run(self):
        try:
            r = requests.get(self.clip_url)

            if r.status_code == 200:
                self.received_data.emit(r)

        except requests.exceptions.RequestException:
            print("Could not connect to clip server!")

if __name__ == "__main__":
    ip = "localhost:5000"  # default clip server IP for testing locally
    if len(sys.argv) == 2:
        ip = sys.argv[1]
    app = QtWidgets.QApplication([])
    window = ClipboardApp(ip)
    sys.exit(app.exec_())

