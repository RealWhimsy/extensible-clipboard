from argparse import ArgumentParser
import mimetypes
import os
import signal
import sys
from urllib.parse import unquote

from flask import Flask

from PyQt5 import QtWidgets
from PyQt5 import QtCore

from clipboard_handler import ClipboardHandler
from networking import ConnectionHandler, ClipSender

"""
This starts the clipboard-server. It acts as a bridge to the OS-clipboard
and synchronizes it with the data from the server. This program can run in
two modes, depending on if it was started with the sync-clipboard option
enabled or not. If it IS enabled, all changes made to the local clipboard
will be forwarded to the server.
If disabled, it will act as a full client and only receive data from the
server while not sending local changes.

The Flask server needs to run in its own thread which adds most of the complex setup otherwise
it will block the whole program.
Built after https://codereview.stackexchange.com/questions/114221/python-gui-by-qtwebkit-and-flask
https://stackoverflow.com/questions/41401386/proper-use-of-qthread-subclassing-works-better-method
"""  # noqa


class MainApp(QtWidgets.QApplication):

    def get_files(self, uri_list):
        """
        Gets all files specified in uri_list from the disk and loads them.
        :return: A list of objects with the file itself, it's mimetype
        and name
        """
        to_return = []
        splits = uri_list.splitlines()
        for s in splits:
            new_file = {}
            path = unquote(s.decode("utf8"))[7:]  # Strings file://
            f = open(path, mode='rb')
            new_file['data'] = f
            new_file['mimetype'] = mimetypes.guess_type(path)[0]
            new_file['filename'] = os.path.split(f.name)[1]
            if new_file['mimetype'] is None:
                new_file['mimetype'] = 'application/octet-stream'
            to_return.append(new_file)
        return to_return

    def on_data_get(self, data):
        """
        Not really sure, why this method is needed,
        might be related to event-loops
        """
        self.clh.put_into_storage(data)

    def send_clipboard_data(self, clip_list):
        """
        Called after the data of the local clipboard has changed.
        Forwards the new content of the clipboard to the server.
        Files will be loaded as needed.
        """
        for clip in clip_list:
            if 'text/uri-list' in clip['mimetype']:
                clip_list += self.get_files(clip['data'])
                break
        self.clip_sender.add_clips_to_server(clip_list)

    def on_id_get(self, _id):
        """
        Called after the clipboard registered itself to the remote server.
        It will receive an id to identify it which should be used in subsequent
        requests to identify itself in the X-C2-sender_id header
        """
        self.clip_sender._id = _id

    def on_current_clip_id_get(self, _id):
        """
        Called when a new clip has been received. Its id will be saved so
        entries received hereafter can be identified as either a different
        representation of the same data or as a completely new clip
        (i.e. another clipboard has been changed and the contents are
        getting synced)
        """
        self.clh.clipboard.current_id = _id

    def main(self):
        """
        Starts the Flask server and itits the clipboard.
        Establishes signal-slot connections
        """
        self.flask_qt.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.flask_qt.start_server)

        # Kills server with whole app
        self.aboutToQuit.connect(self.server_thread.terminate)
        # Makes C-c usable in console, because QT would block it normally
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.clh.clipboard.clipboard_changed_signal.connect(
                self.send_clipboard_data)
        # Cannot put it into self.flask_qt because run() blocks anything
        self.flask_qt.new_item_signal.connect(self.on_data_get)
        self.flask_qt.recipient_id_got.connect(self.on_id_get)
        self.server_thread.start()

    def __init__(self, argv):
        super(MainApp, self).__init__(argv)
        parser = ArgumentParser()
        parser.add_argument('-p', '--port', type=int, dest='port',
                            help='Port THIS server shall listen on, \
                                  defaults to 12345', default=12345)
        parser.add_argument('-d', '--domain', type=str, dest='domain',
                            help='URL THIS server can be reached under, \
                                  must contain specified port, \
                                  defaults to localhost',
                                  default='http://localhost')
        parser.add_argument('-s', '--sync-clipboard', type=bool,
                            dest='sync_clipboard', default=False,
                            help='If True, content of clipboard will be \
                            monitored and changes will be sent to server. \
                            Defaults to False')
        parser.add_argument('-c', '--clipserver', type=str, dest='clipserver',
                            help='URL this server can register itself \
                                  to the clipboard-server', required=True)
        self.args = parser.parse_args()

        self.flask_server = Flask(__name__)
        self.flask_qt = ConnectionHandler(
                self.flask_server,
                self.args.port,
                self.args.clipserver,
                self.args.domain)
        self.server_thread = QtCore.QThread()

        # Connection to system clipboard
        self.clh = ClipboardHandler(self, self.args.sync_clipboard)
        self.clip_sender = ClipSender(
                self.args.clipserver,
                self.on_current_clip_id_get)


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    q_app = MainApp(sys.argv)
    q_app.main()
    sys.exit(q_app.exec_())
