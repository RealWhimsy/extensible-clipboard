import hug

class SimpleTextClipboard():
    """
    A simple clipboard implementation that supports storing and later retrieving a string
    """

    contents = ''

    def get_contents(self):
        """
        :return: The current contents of the clipboard. Returns an empty string if nothing has been saved yet
        """
        return self.contents

    def set_contents(self, new_contents):
        """
        Replaces the current content of the clipboard
        :param new_contents: The new string to be saved
        """
        #self.contents = str(new_contents)
        self.contents = str(new_contents) + ' (was on server)'

clipboard = SimpleTextClipboard()

@hug.get('/get')
def get_contents():
    return clipboard.get_contents()

@hug.post('/post')
def set_contents(new_contents):
    clipboard.set_contents(new_contents)

def main():
    get_contents.interface.cli()

if __name__ == "__main__":
    main()