import sys
from PyQt5 import QtWidgets
from gui import GUI
from config import Log


def main():
    Log()
    app = QtWidgets.QApplication(sys.argv)
    GUI()
    app.exec_()


if __name__ == "__main__":
    sys.exit(main())
