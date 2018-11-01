import signal
import sys
import threading

from flask import Flask, request
from flask_restful import Resource, Api

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread

from clipboard_handler import ClipboardHandler


app = Flask(__name__)
api = Api(app)
clipboard_handler = ClipboardHandler()

class Clip(Resource):

    def get(self, clip_id=None):
        if clip_id is None:
            return {'message': 'nothing specified'}
        return {'clip_id': clip_id}

    def post(self, clip_id=None):
        if clip_id is not None:
            return {'message': 'clip already exists, use PUT to update'}
        print('saving on server')
        content = request.form['clip']
        print(content)
        return {'saved': content}
        #save_on_server()
        #clh.save_in_clipboard()
        

api.add_resource(Clip, '/clip/', '/clip/<string:clip_id>')

# Built after https://codereview.stackexchange.com/questions/114221/python-gui-by-qtwebkit-and-flask

class FlaskThread(QThread):
    
    def __init__(self):
        QThread.__init__(self)
        self.app = app

    def __del__(self):
        self.wait()

    def run(self):
        self.app.run(debug=True, use_reloader=False)


def main():
    q_app = QtWidgets.QApplication(sys.argv)
    webapp = FlaskThread()
    webapp.start()

    q_app.aboutToQuit.connect(webapp.terminate)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    return q_app.exec()

#_thread.start_new_thread(main, () )

if __name__ == "__main__":
    sys.exit(main())
