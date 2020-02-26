import sys
import logging
from logging.config import fileConfig
from PyQt5 import QtWidgets
from gui import MainWindow


def main():
    fileConfig("config/logging_config.ini")
    logger = logging.getLogger(__name__)
    logger.info("Logging Initialized")
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    sys.exit(main())
