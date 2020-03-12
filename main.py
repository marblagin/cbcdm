import sys
from PyQt5 import QtWidgets
from gui import Ui_MainWindow
from config import Log


def main():
    Log()
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    if window.auth_config.first_setup:
        window.api_info_dialog.show()
    app.exec_()


if __name__ == "__main__":
    sys.exit(main())
