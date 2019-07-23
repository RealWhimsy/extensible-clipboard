#!/usr/bin/python3
import sys

from PyQt5 import uic, QtWidgets, QtCore
import time

import os

import subprocess

#
#
# CONSTANTS
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300
STR_APP_NAME = 'Extensible Clipboard Client'
STR_UI_PATH = './client.ui'


#
class ClipboardClientController(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi(STR_UI_PATH, self)
        self.ui.show()
        self.ui.btn_connect.pressed.connect(self.on_start_pressed)
        self.ui.edit_server_address.textChanged.connect(self.on_text_entered)

        self.server_address = None

    # UI Event Handlers

    def on_start_pressed(self):
        self.start_server(
            self.server_address
        )

    def on_text_entered(self, content):
        # TODO: evaluate, whether the input is correct
        # TODO: add http:// and / to address
        self.server_address = content

    # Actions

    def start_server(self, address):
        args = [
           'python3',
            os.path.abspath(os.path.dirname(__file__))+'/clipboard_server/main.py',
            '--port', '5555',
            '--domain', 'public',
            '--clipserver={}'.format(address),
            '--sync-clipboard', 'True'
        ]
        # os.spawnl(os.P_NOWAIT, args)

        command = "python3 ./clipboard_server/main.py --port 5555 --domain=public --clipserver={} --sync-clipboard True &"
        command = command.format(address)
        list = command.split()

        p = subprocess.call(command, shell=True)

        # process = subprocess.Popen(args)

        #while process.poll() is None:
        #    pass

        # process.start()


        #    self.set_connected(True)
             # print(proc.stdout.read())
        #process
        #print(os.path.abspath(os.path.dirname(__file__)))
        #os.chdir(os.path.abspath(os.path.dirname(__file__)+'./clipboard_server'))
        #q_app = MainApp(args)
        #q_app.main()
        #sys.exit(q_app.exec_())


        #str_format = "python3 ./clipboard_server/main.py --port 5555 --domain=public --clipserver={} --sync-clipboard True"
        #os.system(str_format.format(address))
    def set_connected(self, is_connected):
        if is_connected == True:
            self.ui.btn_connect.setDisabled(True)
            self.repaint()


    # Set the display content to the value of str_display and repaint
    def update_display(self):
        #self.ui.display_num.setText(str(val))
        self.update()


    #
    #
    # INPUT BIND FUNCTIONS
    """
    # Connect to GUI Events
    def bind_buttons(self):
        # get all buttons
        # https://stackoverflow.com/questions/13725704/grabbing-all-qpushbutton-in-a-pyqt-python-ui-file 8.5.19
        buttons = self.ui.findChildren(QtWidgets.QPushButton)
        for btn in buttons:
            # ignore first parameter of lambda function (specific for button callbacks)
            # https://stackoverflow.com/questions/18836291/lambda-function-returning-false 8.5.19
            btn.pressed.connect(lambda bound_btn=btn: self.slot_resolve_button_press(bound_btn.objectName()))
            # btn.released.connect(lambda bound_btn=btn: self.slot_resolve_mouserelease(bound_btn.objectName()))

    # bind keypress signals to the resolve function
    def bind_keypress(self):
        self.key_pressed_signal.connect(self.slot_resolve_keypress)

    # Bind keypress to signal
    # https://stackoverflow.com/questions/27475940/pyqt-connect-to-keypressevent, 8.5.19
    def keyPressEvent(self, event):
        super(ClipboardClientController, self).keyPressEvent(event)
        self.key_pressed_signal.emit(event.key())
    """


def main():
    window = ClipboardClientController()
    window.setWindowTitle(STR_APP_NAME)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main()
    sys.exit(app.exec_())
