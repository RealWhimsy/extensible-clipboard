import signal
import sys

from flask import Flask
from flask_restful import Api

from PyQt5 import QtWidgets
from PyQt5 import QtCore

from clipboard_handler import ClipboardHandler
from database import ClipDatabase
from resources import Clip

"""
Built after https://codereview.stackexchange.com/questions/114221/python-gui-by-qtwebkit-and-flask
https://stackoverflow.com/questions/41401386/proper-use-of-qthread-subclassing-works-better-method
"""  # noqa


class FlaskQt(QtCore.QObject):

    data = QtCore.pyqtSignal(object)

    def __init__(self, flask_app, database):
        super(QtCore.QObject, self).__init__()
        self.app = flask_app
        self.db = database

    def start_server(self):
        self.app.run(debug=True, use_reloader=False)

    def emit_data(self, data):
        self.data.emit(data)

    def save_in_database(self, data):
        id = self.db.save_clip(data)
        return id

    def get_clip_by_id(self, id):
        return self.db.get_clip_by_id(id)

    def get_all_clips(self):
        return self.db.get_all_clips()


class MainApp(QtWidgets.QApplication):

    def dummy(self, data):
        # Not really sure, why this method is needed,
        # might be related to event-loops
        self.clh.put_into_storage(data)

    def add_resources(self):
        # Creates endpoint for REST-Api
        self.api.add_resource(Clip,
                              '/clip/', '/clip/<string:clip_id>',
                              resource_class_kwargs={
                                    'server': self.server_qt
                                  }
                              )

    def main(self):
        self.server_qt.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.server_qt.start_server)

        # Kills server with whole app
        self.aboutToQuit.connect(self.server_thread.terminate)
        # Makes C-c usable in console, because QT would block it normally
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.server_qt.data.connect(self.dummy)
        self.add_resources()
        self.server_thread.start()

    def __init__(self, argv):
        super(MainApp, self).__init__(argv)

        # The flask-server itself
        self.flask_server = Flask(__name__)
        # Restful-Flask server
        self.api = Api(self.flask_server)
        # Database for saving clips, currently mongo
        self.database = ClipDatabase()

        # Qt-Object the server gets wrapped in
        self.server_qt = FlaskQt(self.flask_server, self.database)
        # QThread, it executes the server
        self.server_thread = QtCore.QThread()
        # Connection to system clipboard
        self.clh = ClipboardHandler(self)


if __name__ == "__main__":
    q_app = MainApp(sys.argv)
    q_app.main()
    sys.exit(q_app.exec_())
