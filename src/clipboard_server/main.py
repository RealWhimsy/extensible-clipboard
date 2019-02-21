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
Built after https://codereview.stackexchange.com/questions/114221/python-gui-by-qtwebkit-and-flask
https://stackoverflow.com/questions/41401386/proper-use-of-qthread-subclassing-works-better-method
"""  # noqa


class MainApp(QtWidgets.QApplication):

    def get_files(self, uri_list):
        to_return = []
        splits = uri_list.splitlines()
        for s in splits:
            new_file = {}
            path = unquote(s)[7:]
            with open(path, mode='rb') as f:
                new_file['data'] = f
                new_file['mimetype'] = mimetypes.guess_type(path)[0]
                to_return.append(new_file)
        return to_return

    def on_data_get(self, data):
        """
        Not really sure, why this method is needed,
        might be related to event-loops
        """
        self.clh.put_into_storage(data)

    def send_clipboard_data(self, clip_list):
        for clip in clip_list:
            if 'text/uri-list' in clip['mimetype']:
                clip_list += self.get_files(clip['data'])
                break;
        self.clip_sender.add_clips_to_server(clip_list)

    def on_id_get(self, _id):
        print('got id {}'.format(_id))
        self.clip_sender._id = _id

    def on_current_clip_id_get(self, _id):
        self.clh.clipboard.current_id = _id
        print('updated id to {}'.format(self.clh.clipboard.current_id))

    def main(self):
        self.flask_qt.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.flask_qt.start_server)

        # Kills server with whole app
        self.aboutToQuit.connect(self.server_thread.terminate)
        # Makes C-c usable in console, because QT would block it normally
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # Cannot put it into self.flask_qt because run() blocks anything
        self.clh.clipboard.clipboard_changed_signal.connect(self.send_clipboard_data)
        self.flask_qt.new_item_signal.connect(self.on_data_get)
        self.flask_qt.recipient_id_got.connect(self.on_id_get)
        self.server_thread.start()

    def __init__(self, argv):
        super(MainApp, self).__init__(argv)
        parser = ArgumentParser()
        parser.add_argument('-p', '--port', type=int, dest='port',
                help='Port THIS server shall listen on, defaults to 12345', default=12345)
        parser.add_argument('-d', '--domain', type=str, dest='domain',
                help='URL THIS server can be reached under, must contain specified port, defaults to localhost',
                default='http://localhost')
        parser.add_argument('-s', '--sync-clipboard', type=bool, dest='sync_clipboard', default=False,
                help='If True, content of clipboard will be monitored and changes will be sent to server. \
                      Defaults to False')
        parser.add_argument('-c', '--clipserver', type=str, dest='clipserver',
                help='URL this server can register itself to the clipboard-server', required=True)
        self.args = parser.parse_args()

        self.flask_server = Flask(__name__)
        self.flask_qt = ConnectionHandler(self.flask_server, self.args.port, self.args.clipserver, self.args.domain)
        self.server_thread = QtCore.QThread()

        # Connection to system clipboard
        self.clh = ClipboardHandler(self, self.args.sync_clipboard)
        self.clip_sender = ClipSender(self.args.clipserver, self.on_current_clip_id_get)


if __name__ == "__main__":
    q_app = MainApp(sys.argv)
    q_app.main()
    sys.exit(q_app.exec_())
