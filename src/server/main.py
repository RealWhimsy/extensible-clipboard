import signal
import sys
import threading

from flask import Flask, request

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread

#from clipboard_handler import ClipboardHandler

app = Flask(__name__)
#clipboard_handler = ClipboardHandler()

@app.route('/')
def get_contents():
    return "Hello world"

@app.route('/post', methods=['POST'])
def set_contents():
    content = request.form['new_contents']
    print('saving on server')
    print(content)
    return content
    #save_on_server()
    #clh.save_in_clipboard()

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
