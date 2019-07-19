#!/usr/bin/python3

import sys

from PyQt5 import uic, QtWidgets, QtCore
import time

#
#
# CONSTANTS
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300
STR_APP_NAME = 'Extensible Clipboard Host'
STR_UI_PATH = './host.ui'



#
# CALCULATOR CONTROLLER
#
# Acts as view controller for the calculator, relaying input events to the logic and updating the visualisation.
#
# Window boilerplate
# https://www.python-forum.de/viewtopic.php?t=32093, 30.04.2019
#
class CalculatorController(QtWidgets.QMainWindow):
    str_display = ''
    # Transform key pressed to signal
    # source: https://stackoverflow.com/questions/27475940/pyqt-connect-to-keypressevent, 8.5.19
    key_pressed_signal = QtCore.pyqtSignal(int)

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = uic.loadUi(STR_UI_PATH, self)
        self.ui.show()

    #
    #
    # DISPLAY FUNCTIONS

    # Set the display content to the value of str_display and repaint
    def update_display(self):
        self.repaint()




def main():
    window = CalculatorController()
    window.setWindowTitle(STR_APP_NAME)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main()
    sys.exit(app.exec_())
