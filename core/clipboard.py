from PyQt5.QtGui import QClipboard


class Clipboard:

    clipboard = None

    def  save(self, data):
        data = str(data)
        #print('saving data: {}'.format(data))
        self.clipboard.setText(data)

    def __init__(self, clip):
        self.clipboard = clip