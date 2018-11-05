import signal
import sys
import threading

from flask import abort, Flask, request
from flask_restful import Resource, Api

from PyQt5 import QtWidgets
from PyQt5 import QtCore

from clipboard_handler import ClipboardHandler
from database import ClipDatabase


class Clip(Resource):

    def __init__(self, **kwargs):
        self.server = kwargs['server']
        

    def get(self, clip_id=None):
        if clip_id is None:
            return {'message': 'nothing specified'}
        clip = self.server.get_clip_by_id(clip_id)
       
        if clip is 'null':
            return abort(404)
        return clip

    def post(self, clip_id=None):
        if clip_id is not None:
            return {'message': 'clip already exists, use PUT to update'}

        content = request.form['clip'] # Automatically sends 400 if no match
        new_item_id = self.server.save_in_database(content)
        self.server.emit_data(content)
        return {'saved': new_item_id}
        


# Built after https://codereview.stackexchange.com/questions/114221/python-gui-by-qtwebkit-and-flask
# https://stackoverflow.com/questions/41401386/proper-use-of-qthread-subclassing-works-better-method

class FlaskThread(QtCore.QObject):
    
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


class MainApp(QtWidgets.QApplication):
    flask_server = None
    app = Flask(__name__)
    flask_thread = None
    api = Api(app)
    clh = None
    database = None

    def dummy(self, data):
        self.clh.put_into_storage(data)

    def main(self):
        self.database = ClipDatabase()
        self.flask_server = FlaskThread(self.app, self.database)
        self.flask_thread = QtCore.QThread()
        self.flask_server.moveToThread(self.flask_thread)
        self.flask_thread.started.connect(self.flask_server.start_server)

        self.aboutToQuit.connect(self.flask_thread.terminate)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.clh = ClipboardHandler(self)

        self.flask_server.data.connect(self.dummy)
        self.api.add_resource(Clip, '/clip/', '/clip/<string:clip_id>',
                resource_class_kwargs={
                    'server': self.flask_server})

        self.flask_thread.start()


if __name__ == "__main__":
    q_app = MainApp(sys.argv)
    q_app.main()
    sys.exit(q_app.exec_())
