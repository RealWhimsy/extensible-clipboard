import signal
import sys

from flask import Flask
from flask_restful import Api

#from PyQt5 import QtWidgets
#from PyQt5 import QtCore

from clipboard_handler import ClipboardHandler
from database import ClipDatabase
from flask_server import FlaskQt
from resources import Clip

"""
Built after https://codereview.stackexchange.com/questions/114221/python-gui-by-qtwebkit-and-flask
https://stackoverflow.com/questions/41401386/proper-use-of-qthread-subclassing-works-better-method
"""  # noqa


class MainApp():

    def dummy(self, data):
        """
        Not really sure, why this method is needed,
        might be related to event-loops
        """
        self.clh.put_into_storage(data)

    def add_resources(self):
        # Creates endpoint for REST-Api
        self.api.add_resource(Clip,
                              '/clip/',
                              '/clip/latest/',
                              '/clip/<uuid:clip_id>',
                              '/clip/<uuid:clip_id>/add_child',
                              '/clip/<uuid:clip_id>/get_alternatives/',
                              resource_class_kwargs={
                                    'server': self.server_qt
                                  }
                              )

    def main(self):
        #self.server_qt.moveToThread(self.server_thread)
        #self.server_thread.started.connect(self.server_qt.start_server)

        # Kills server with whole app
        #self.aboutToQuit.connect(self.server_thread.terminate)
        # Makes C-c usable in console, because QT would block it normally
        #signal.signal(signal.SIGINT, signal.SIG_DFL)

        #self.server_qt.data_signal.connect(self.dummy)
        self.add_resources()
        #self.server_thread.start()
        self.server_qt.start_server()

    def __init__(self, argv):
        #super(MainApp, self).__init__(argv)

        # The flask-server itself
        self.flask_server = Flask(__name__)
        # Restful-Flask server
        self.api = Api(self.flask_server)
        # Database for saving clips, currently mongo
        self.database = ClipDatabase()

        # Qt-Object the server gets wrapped in
        self.server_qt = FlaskQt(self.flask_server, self.database)
        # QThread, it executes the server
        #self.server_thread = QtCore.QThread()
        # Connection to system clipboard
        #self.clh = ClipboardHandler(self)


if __name__ == "__main__":
    q_app = MainApp(sys.argv)
    q_app.main()
    #sys.exit(q_app.exec_())
