#!/usr/bin/python3
import sys

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
import time

import os
import signal

import subprocess

#
#
# CONSTANTS
from clipboard_server.main import ClipboardServerApp

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300
STR_APP_NAME = 'Extensible Clipboard Client'
STR_UI_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) + '/extclipgui.ui'
STR_CLIPBOARD_SCRIPT_PATH = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) + '/clipboard_server/main.py'


#
class ClipboardClientController(QMainWindow):

    def __init__(self, ctx):
        super(ClipboardClientController, self).__init__()
        self.ctx = ctx
        # self.ui = uic.loadUi(STR_UI_PATH, self)
        self.ui = uic.loadUi(ctx.get_resource('ui/extclipgui.ui'), self)
        self.ui.show()
        self.ui.btn_connect.pressed.connect(self.on_connect_pressed)
        self.ui.btn_disconnect.pressed.connect(self.on_disconnect_pressed)
        self.ui.edit_server_address.textChanged.connect(self.update_model)
        self.ui.edit_port.textChanged.connect(self.update_model)
        self.ui.check_sync.stateChanged.connect(self.update_model)

        self.server_address = self.ui.edit_server_address.text()
        self.own_port = self.ui.edit_port.text()
        self.is_syncing = self.ui.check_sync.isChecked()
        self.clipboard_process = None
        self.domain = "<UNKNOWN>"

        self.set_connected(False)

    # UI Event Handlers

    def on_connect_pressed(self):
        self.start_server(
            self.server_address
        )

    def on_disconnect_pressed(self):
        os.killpg(os.getpgid(self.clipboard_server.pid), signal.SIGTERM)
        self.set_connected(False)


    def update_model(self, data):
        self.server_address = self.ui.edit_server_address.text()
        self.own_port = self.ui.edit_port.text()
        self.is_syncing = self.ui.check_sync.isChecked()

    # legacy
    def on_text_entered(self, content):
        # TODO: evaluate, whether the input is correct
        # TODO: add http:// and / to address
        pass

    def closeEvent(self, QCloseEvent):
        if self.clipboard_server  is not None:
            os.killpg(os.getpgid(self.clipboard_server.pid), signal.SIGTERM)


    # Actions

    def start_server(self, address):
        try:
            port = self.ui.edit_port.text()
            q_app = ClipboardServerApp(port, address, "public", True, sys.argv, self.ctx.app)
            q_app.main()
        except:
            print("Could not start server")
        # q_app.main()
        #command = "python3 " + STR_CLIPBOARD_SCRIPT_PATH + " --port={} --domain=public --clipserver={} --sync-clipboard True"
        #command = command.format(self.ui.edit_port.text(), address)

        #self.clipboard_server = subprocess.Popen(command, shell=True)
        #if self.clipboard_server is not None:
            #self.set_connected(True)
            #self.update_display()

        """
        try:
            pass
            self.clipboard_server = ClipboardServerApp(self.own_port, address, "public", self.is_syncing, sys.argv)
            self.clipboard_server.main()
            self.domain = self.clipboard_server.flask_qt.domain
            self.update_display()
        except:
            print("Error connecting!")
            # TODO: error handling and feedback!
        """

    def set_connected(self, is_connected):
        self.ui.btn_connect.setDisabled(is_connected)
        self.ui.btn_disconnect.setDisabled(not is_connected)

        self.ui.edit_port.setDisabled(is_connected)
        self.ui.edit_server_address.setDisabled(is_connected)
        self.ui.check_sync.setDisabled(is_connected)

        if is_connected == True:
            self.ui.btn_connect.setText("Connected!")
        else:
            self.ui.btn_connect.setText("Connect")
        self.repaint()


    # Set the display content to the value of str_display and repaint
    def update_display(self):
        self.lbl_port_3.setText(self.domain)
        self.update()
        self.repaint()


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
    app = QApplication(sys.argv)
    main()
    #sys.exit(app.exec_())
    app.exec()