import hug
import sys
import _thread

from clipboard_handler import ClipboardHandler

@hug.get('/get')
def get_contents():
    return "Hello world"

@hug.post('/post')
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
    print("in main")
    start_clipboard_handler()

#_thread.start_new_thread(main, () )

if __name__ == "__main__":
    print('called')
    main()
