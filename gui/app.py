import sys

from PyQt5 import uic
from PyQt5 import QtWidgets, QtGui

ui_file = "tester.ui"


class MyApp(QtWidgets.QMainWindow):


    def paste_clicked(self):
        if self.listWidget.currentItem() is not None:
            print(self.listWidget.currentItem().text())

    def copy_clicked(self):
        pass

    def __init__(self):
        super().__init__()
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