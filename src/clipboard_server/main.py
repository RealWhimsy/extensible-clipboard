from argparse import ArgumentParser
import signal
import sys

from flask import Flask

from PyQt5 import QtWidgets
from PyQt5 import QtCore

from clipboard_handler import ClipboardHandler
from networking import ConnectionHandler

"""
Built after https://codereview.stackexchange.com/questions/114221/python-gui-by-qtwebkit-and-flask
https://stackoverflow.com/questions/41401386/proper-use-of-qthread-subclassing-works-better-method
"""  # noqa


class MainApp(QtWidgets.QApplication):

    def dummy(self, data):
        """
        Not really sure, why this method is needed,
        might be related to event-loops
        """
        self.clh.put_into_storage(data)

    def main(self):
        self.flask_qt.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.flask_qt.start_server)

        # Kills server with whole app
        self.aboutToQuit.connect(self.server_thread.terminate)
        # Makes C-c usable in console, because QT would block it normally
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.flask_qt.new_item_signal.connect(self.dummy)
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
        print(self.args)

        self.flask_server = Flask(__name__)
        self.flask_qt = ConnectionHandler(self.flask_server, self.args.port, self.args.clipserver, self.args.domain)
        self.server_thread = QtCore.QThread()

        # Connection to system clipboard
        self.clh = ClipboardHandler(self, self.args.sync_clipboard)


if __name__ == "__main__":
    q_app = MainApp(sys.argv)
    q_app.main()
    sys.exit(q_app.exec_())
