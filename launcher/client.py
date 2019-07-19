#!/usr/bin/python3

import sys

from PyQt5 import uic, QtWidgets, QtCore
import time

#
#
# CONSTANTS
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 300
STR_APP_NAME = 'Simple Calc'
STR_UI_PATH = './calculator.ui'
CHARS_OPERATORS = ['+', '-', '*', '/', '.']


# Global Decorator function for logging
def log(event):
    def log_decorator(func_in):
        def wrapper(*args):
            log_format = '{},"{}","{}"'
            print(log_format.format(time.time(), event.strip(), args[1]))
            func_in(*args)

        return wrapper

    return log_decorator


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
        self.bind_buttons()
        self.bind_keypress()
        self.logic = CalculatorModel()

        log_format = '{},"{}","{}"'
        print(log_format.format('"Timestamp"', "EventType", "EventValue"))

    #
    #
    # DISPLAY FUNCTIONS

    # Set the display content to the value of str_display and repaint
    def update_display(self):
        if self.str_display == '':
            val = 0
        else:
            val = self.str_display
        self.ui.display_num.setText(str(val))
        self.repaint()

    #
    #
    # INPUT RESOLVERS

    # Handle button press events
    @log('button_pressed')
    def slot_resolve_button_press(self, str_btn_id):
        # Send handling
        # http://zetcode.com/gui/pyqt5/eventssignals/ (8.5.19)
        operation_id = str_btn_id.split('_')[-1:][0]
        if operation_id.isdigit() or (operation_id in CHARS_OPERATORS):
            self.str_display = self.logic.add_char_to_input(operation_id)
        elif operation_id == 'enter':
            self.str_display = self.logic.execute()
        elif operation_id == 'deletelast':
            self.str_display = self.logic.remove_last_char()
        elif operation_id == 'clear':
            self.str_display = self.logic.clear_input()
        self.update_display()

    # Handle Key press events
    @log('key_pressed')
    def slot_resolve_keypress(self, keycode):
        if keycode == 16777219:
            self.str_display = self.logic.remove_last_char()
        elif keycode == 16777220:
            self.str_display = self.logic.execute()
        elif keycode == 16777216:
            self.str_display = self.logic.clear_input()
        else:
            try:
                char_input = chr(keycode)
                if char_input.isdigit() or char_input in CHARS_OPERATORS:
                    self.str_display = self.logic.add_char_to_input(char_input)
            except ValueError:
                pass
                # print("Invalid keycode")
        self.update_display()

    @log('button_released')
    def slot_resolve_mouserelease(self, btn):
        pass

    #
    #
    # INPUT BIND FUNCTIONS

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
        super(CalculatorController, self).keyPressEvent(event)
        self.key_pressed_signal.emit(event.key())


#
# CALCULATOR MODEL
#
# Contains calculator data model and computation logic.
#
class CalculatorModel:

    def __init__(self):
        self.str_input = ''

    # Add a new character (valid: 0-9, -, +, *, /, .)
    def add_char_to_input(self, char_in):
        self.str_input += str(char_in)
        return self.str_input

    # Remove the last character
    def remove_last_char(self):
        if len(self.str_input) > 0:
            self.str_input = self.str_input[:-1]
        return self.str_input

    # Remove all characters from input
    def clear_input(self):
        self.str_input = ''
        return '0'

    # Execute the calculations
    def execute(self):
        if self.str_input is not '':
            try:
                result = eval(self.str_input)
                self.str_input = str(result)
                return result
            except:
                print("SYNTAX ERROR")
                return self.str_input
        else:
            return '0'


def main():
    window = CalculatorController()
    window.setWindowTitle(STR_APP_NAME)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main()
    sys.exit(app.exec_())
