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

        self.flask_server = Flask(__name__)
        self.flask_qt = ConnectionHandler(self.flask_server)
        self.server_thread = QtCore.QThread()

        # Connection to system clipboard
        self.clh = ClipboardHandler(self)


if __name__ == "__main__":
    q_app = MainApp(sys.argv)
    q_app.main()
    sys.exit(q_app.exec_())
