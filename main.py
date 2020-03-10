import sys
from PyQt5 import QtWidgets
from gui import Ui_MainWindow
from config import Log


def main():
    Log()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    app.exec_()


if __name__ == "__main__":
    sys.exit(main())
