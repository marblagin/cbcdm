import logging
from api import ApiRequest, Response, Auth
from config import AuthConfig
from data import DataHandler
from PyQt5 import uic, QtWidgets, QtCore
from pandas import DataFrame


class MainWindow(QtWidgets.QFrame):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('cbcdm.ui', self)
        self.setWindowTitle("CBCDM")
        self.resize(1000, 700)

        # Data Request and Load
        self.auth_config = AuthConfig()
        self.auth = Auth(self.auth_config.config, self.auth_config.profiles[0])
        self.request = ApiRequest(self.auth)
        self.response = Response(self.request.http_request())
        if self.request.success:
            data_handler = DataHandler(data_file="devices.json", data_path="data")
            data_handler.file_dump(self.response.content)
            self.data_frame = DataFrame(data_handler.read_json_data_results())
            self.results_model = PandasModel(self.data_frame)

        # Device Table
        self.DevicesTable = QtWidgets.QTableView(self)
        self.DevicesTable.setGeometry(QtCore.QRect(20, 110, 731, 481))
        self.DevicesTable.setToolTipDuration(0)
        self.DevicesTable.setObjectName("DevicesTable")
        self.DevicesTable.setModel(self.results_model)
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
            self.data_frame = DataFrame(data_handler.read_json_data_results())
            self.results_model = PandasModel(self.data_frame)
        self.DevicesTable.setModel(self.results_model)
        self.DevicesTable.create()

    # Todo: need to create all the widgets functions


class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None