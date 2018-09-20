import hug
import sys

import clipboard_handler 

@hug.get('/get')
def get_contents():
    return "Hello world"

@hug.post('/post')
def set_contents(new_contents):
    pass
"""
def start_clipboard_handler():
    ""
    Starts a QT-Application which will handle actions on the system clipboard
    ""
    print("before construction chandler")
    cl = clipboard_handler.ClipboardHandler()

def main():
    print("in main")
    start_clipboard_handler()

main()
"""
if __name__ == "__main__":
    main()
