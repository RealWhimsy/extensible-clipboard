import sys

from PyQt5 import uic
from PyQt5 import QtWidgets, QtGui

from core.event_handler import EventHandler

ui_file = "tester.ui"


class MyApp(QtWidgets.QMainWindow):

    event_handler = None


    def paste_clicked(self):
        self.event_handler.retrieve_from_storage()

    def copy_clicked(self):
        current_item = self.listWidget.currentItem()
        if current_item is not None:
            self.event_handler.put_into_storage(current_item.text())

    def __init__(self):
        super().__init__()
        self.event_handler = EventHandler(app)
        uic.loadUi(ui_file, self)

        self.listWidget.addItem('Es war einmal ein altes Schloss')
        self.listWidget.addItem('Und Kunibert, so hieß der Boss')
        self.listWidget.addItem('Er hatte Mägde, hatte Knechte')
        self.listWidget.addItem('Und eine Frau, das war das Schlechte')

        self.PasteButton.clicked.connect(self.paste_clicked)
        self.CopyButton.clicked.connect(self.copy_clicked)

        self.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = MyApp()
    widget.show()
    sys.exit(app.exec_())