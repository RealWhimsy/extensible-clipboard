import hug
import sys
import _thread

from clipboard_handler import ClipboardHandler

@hug.get('/get')
def get_contents():
    return "Hello world"

@hug.post('/post')
def set_contents(new_contents):
    pass

def start_clipboard_handler():
    """
    Starts a QT-Application which will handle actions on the system clipboard
    """
    cl = ClipboardHandler()

def main():
    print("in main")
    start_clipboard_handler()

_thread.start_new_thread(main, () )
