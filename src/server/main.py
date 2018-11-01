import signal
import sys
import threading

from flask import Flask, request
from flask_restful import Resource, Api

from PyQt5 import QtWidgets
from PyQt5 import QtCore
#from QtCore import QThread, pyqtSignal

from clipboard_handler import ClipboardHandler


class Clip(Resource):

    def __init__(self, **kwargs):
        self.clipboard_handler = kwargs['handler']
        

    def get(self, clip_id=None):
        if clip_id is None:
            return {'message': 'nothing specified'}
        return {'clip_id': clip_id}

    def post(self, clip_id=None):
        if clip_id is not None:
            return {'message': 'clip already exists, use PUT to update'}
        content = request.form['clip']
        #save_on_server()
        self.clipboard_handler.emit_data(content)
        return {'saved': content}
        


# Built after https://codereview.stackexchange.com/questions/114221/python-gui-by-qtwebkit-and-flask

class FlaskThread(QtCore.QObject):
    
    data = QtCore.pyqtSignal(object)

    def __init__(self, flask_app):
        super(QtCore.QObject, self).__init__()
        self.app = flask_app

    def __del__(self):
        self.wait()

    def start_server(self):
        self.app.run(debug=True, use_reloader=False)

    def emit_data(self, data):
        print('in emit_data {}'.format(data))
        self.data.emit(data)



class MainApp(QtWidgets.QApplication):
    app = Flask(__name__)
    flask_thread = None
    api = Api(app)
    clh = None

    def dummy(self, data):
        print('in dummy')
        self.clh.put_into_storage(data)

    def main(self):
        webapp = FlaskThread(self.app)
        self.flask_thread = QtCore.QThread()
        webapp.moveToThread(self.flask_thread)
        self.flask_thread.started.connect(webapp.start_server)

        self.aboutToQuit.connect(self.flask_thread.terminate)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.clh = ClipboardHandler(self)

        webapp.data.connect(self.dummy)
        self.api.add_resource(Clip, '/clip/', '/clip/<string:clip_id>', resource_class_kwargs={'handler': webapp})

        self.flask_thread.start()


if __name__ == "__main__":
    q_app = MainApp(sys.argv)
    q_app.main()
    sys.exit(q_app.exec_())
