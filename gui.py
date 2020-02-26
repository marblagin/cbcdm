import logging
from api import ApiRequest, Response, Auth
from config import AuthConfig, get_sensor_info
from data import DataHandler
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem


class MainWindow(QtWidgets.QFrame):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('cbcdm.ui', self)
        self.setWindowTitle("CBCDM")
        self.resize(930, 640)

        self.auth_config = AuthConfig()
        self.auth = Auth(self.auth_config.config, self.auth_config.profiles[0])
        self.request = ApiRequest(self.auth)
        self.response = Response(self.request.http_request())
        if self.request.success:
            data_handler = DataHandler(data_file="devices.json")
            data_handler.file_dump(self.response.content)

        self.DevicesTable = QtWidgets.QTableWidget(self)
        self.DevicesTable.setGeometry(QtCore.QRect(20, 110, 731, 481))
        self.DevicesTable.setToolTipDuration(0)
        self.DevicesTable.setObjectName("DevicesTable")
        self.DevicesTable.setRowCount(int(self.response.total_results) + 1)

        # Todo find a way to return a list of all attrs of a calss rather than using a text file
        sensor_info = get_sensor_info()
        self.DevicesTable.setColumnCount(sensor_info.__len__())
        for x in range(sensor_info.__len__()):
            self.DevicesTable.setItem(0, x, QTableWidgetItem(sensor_info[x]))
        for x in range(int(self.response.total_results)):
            # Todo find a way to assign each point of device data to the right column
            self.DevicesTable.setItem(x+1, 0, QTableWidgetItem(self.response.all_devices[x].name))
        self.DevicesTable.create()

        self.Refresh = QtWidgets.QPushButton(self)
        self.Refresh.setGeometry(QtCore.QRect(150, 600, 89, 25))
        self.Refresh.setObjectName("Refresh")
        self.Refresh.setText("Refresh")
        self.Refresh.clicked.connect(self.refresh_data)

        self.Export = QtWidgets.QPushButton(self)
        self.Export.setGeometry(QtCore.QRect(20, 600, 121, 25))
        self.Export.setObjectName("Export")
        self.Export.setText("Export")

        self.APIFrame = QtWidgets.QFrame(self)
        self.APIFrame.setGeometry(QtCore.QRect(20, 20, 341, 81))
        self.APIFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.APIFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.APIFrame.setObjectName("APIFrame")

        self.APIComboBox = QtWidgets.QComboBox(self.APIFrame)
        self.APIComboBox.setGeometry(QtCore.QRect(20, 40, 301, 25))
        self.APIComboBox.setEditable(False)
        logging.debug('Number of profiles to load: ' + str(self.auth_config.get_num_profiles()))
        for x in range(self.auth_config.get_num_profiles()):
            self.APIComboBox.addItem(self.auth_config.profiles[x])
            logging.debug('Adding profile ' + str(self.auth_config.profiles[x]) + ' to combo box')
        self.APIComboBox.setObjectName("APIComboBox")

        # Todo add function to sync data to selected api

        self.APITitle = QtWidgets.QLabel(self.APIFrame)
        self.APITitle.setGeometry(QtCore.QRect(20, 10, 81, 17))
        self.APITitle.setObjectName("APITitle")

        self.ColumnFrame = QtWidgets.QFrame(self)
        self.ColumnFrame.setGeometry(QtCore.QRect(760, 110, 151, 481))
        self.ColumnFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ColumnFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ColumnFrame.setObjectName("ColumnFrame")

        self.Name = QtWidgets.QCheckBox(self.ColumnFrame)
        self.Name.setGeometry(QtCore.QRect(10, 10, 92, 23))
        self.Name.setObjectName("Name")

        self.UninstallCode = QtWidgets.QCheckBox(self.ColumnFrame)
        self.UninstallCode.setGeometry(QtCore.QRect(10, 40, 121, 23))
        self.UninstallCode.setObjectName("UninstallCode")

    def refresh_data(self):
        logging.info('Refreshing data')
        logging.debug('ComboBox Set to index ' + str(self.APIComboBox.currentIndex()))
        logging.debug('Profile selected: ' + self.APIComboBox.itemText(self.APIComboBox.currentIndex()))
        self.request = ApiRequest(self.auth_config.load_profile(self.APIComboBox.itemText(self.APIComboBox.currentIndex())))
        self.response = Response(self.request.http_request())

        # Todo Consider removing the constant data dumping
        if self.request.success:
            data_handler = DataHandler(data_file="devices.json")
            data_handler.file_dump(self.response.content)
        self.DevicesTable.setRowCount(int(self.response.total_results) + 1)
        self.DevicesTable.setColumnCount(1)
        self.DevicesTable.setItem(0, 0, QTableWidgetItem("Name"))
        for x in range(int(self.response.total_results)):
            self.DevicesTable.setItem(x+1, 0, QTableWidgetItem(self.response.all_devices[x].name))
        self.DevicesTable.create()

    # Todo: need to create all the widgets functions
