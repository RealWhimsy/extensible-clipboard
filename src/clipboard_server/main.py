import signal
import sys


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
        #self.server_qt.moveToThread(self.server_thread)
        #self.server_thread.started.connect(self.server_qt.start_server)

        # Kills server with whole app
        #self.aboutToQuit.connect(self.server_thread.terminate)
        # Makes C-c usable in console, because QT would block it normally
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        #self.server_qt.data_signal.connect(self.dummy)
        #self.add_resources()
        #self.server_thread.start()
        #self.server_qt.start_server()
        self.connections.register_to_server()

    def __init__(self, argv):
        super(MainApp, self).__init__(argv)

        # Connection to system clipboard
        self.clh = ClipboardHandler(self)
        self.connections = ConnectionHandler()


if __name__ == "__main__":
    q_app = MainApp(sys.argv)
    q_app.main()
    sys.exit(q_app.exec_())
