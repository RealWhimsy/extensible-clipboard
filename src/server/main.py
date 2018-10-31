import sys
import threading

from flask import Flask
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread

from clipboard_handler import ClipboardHandler

app = Flask(__name__)

@app.route('/')
def get_contents():
    return "Hello world"

class FlaskThread(QThread):
    
    def __init__(self):
        QThread.__init__(self)
        self.app = app

    def __del__(self):
        self.wait()

    def run(self):
        self.app.run()


def set_contents(new_contents):
    print('saving on server')
    save_on_server()
    clh.save_in_clipboard()

def start_clipboard_handler():
    """
    Starts a QT-Application which will handle actions on the system clipboard
    """
    clh = ClipboardHandler()

def main():
    q_app = QtWidgets.QApplication(sys.argv)
    webapp = FlaskThread()
    webapp.start()

    q_app.aboutToQuit.connect(webapp.terminate)
    return q_app.exec()

#_thread.start_new_thread(main, () )

if __name__ == "__main__":
    sys.exit(main())
