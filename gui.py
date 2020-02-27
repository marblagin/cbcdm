import logging
from api import ApiRequest, Response, Auth
from config import AuthConfig
from data import DataHandler
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import QObject, pyqtSignal
from pandas import DataFrame


class MainWindow(QtWidgets.QFrame):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi('ui/cbcdmv1.1.ui', self)
        self.setWindowTitle("CBCDM")

        # Initializes UI objects
        self.DevicesTable = QtWidgets.QTableView(self)
        self.DevicesTable.setGeometry(QtCore.QRect(20, 110, 991, 691))
        self.DevicesTable.setProperty("toolTipDuration", 0)
        self.DevicesTable.setObjectName("DevicesTable")
        self.Refresh = QtWidgets.QPushButton(self)
        self.Refresh.setGeometry(QtCore.QRect(370, 60, 121, 25))
        self.Refresh.setObjectName("Refresh")
        self.Export = QtWidgets.QPushButton(self)
        self.Export.setGeometry(QtCore.QRect(370, 20, 121, 25))
        self.Export.setObjectName("Export")
        self.APIFrame = QtWidgets.QFrame(self)
        self.APIFrame.setGeometry(QtCore.QRect(20, 10, 341, 81))
        self.APIFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.APIFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.APIFrame.setObjectName("APIFrame")
        self.APIComboBox = QtWidgets.QComboBox(self.APIFrame)
        self.APIComboBox.setGeometry(QtCore.QRect(20, 40, 301, 25))
        self.APIComboBox.setEditable(False)
        self.APIComboBox.setProperty("currentText", "")
        self.APIComboBox.setObjectName("APIComboBox")
        self.APITitle = QtWidgets.QLabel(self.APIFrame)
        self.APITitle.setGeometry(QtCore.QRect(20, 10, 81, 17))
        self.APITitle.setObjectName("APITitle")
        self.ColumnList = QtWidgets.QListWidget(self)
        self.ColumnList.setGeometry(QtCore.QRect(1020, 110, 256, 691))
        self.ColumnList.setObjectName("ColumnList")
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Checked)
        self.ColumnList.addItem(item)
        self.NumFoundLabel = QtWidgets.QLabel(self)
        self.NumFoundLabel.setGeometry(QtCore.QRect(520, 60, 181, 21))
        self.NumFoundLabel.setObjectName("NumFoundLabel")

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        # Data Request and Load
        self.auth_config = AuthConfig()
        self.auth = Auth(self.auth_config.config, self.auth_config.profiles[0])
        self.request = ApiRequest(self.auth)
        self.response = Response(self.request.http_request())
        if self.request.success:
            self.data_handler = DataHandler(data_file="devices.json", data_path="data")
            if self.data_handler.file_dump(self.response.content):
                self.data_frame = DataFrame(self.data_handler.read_json_data_results())
                self.edited_data_frame = self.data_frame
                self.results_model = PandasModel(self.data_frame)

        # Environment Variables
        self.filtered = False

        # Assign data to UI elements
        self.refresh_elements()

        logging.debug('Number of profiles to load: ' + str(self.auth_config.get_num_profiles()))
        for x in range(self.auth_config.get_num_profiles()):
            self.APIComboBox.addItem(self.auth_config.profiles[x])
            logging.debug('Adding profile ' + str(self.auth_config.profiles[x]) + ' to combo box')

        self.bind_buttons()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Form"))
        self.Refresh.setText(_translate("MainWindow", "Refresh"))
        self.Export.setText(_translate("MainWindow", "Export to CSV"))
        self.APITitle.setText(_translate("MainWindow", "Select API:"))
        __sortingEnabled = self.ColumnList.isSortingEnabled()
        self.ColumnList.setSortingEnabled(False)
        item = self.ColumnList.item(0)
        item.setText(_translate("MainWindow", "Example List Value"))
        self.ColumnList.setSortingEnabled(__sortingEnabled)
        self.NumFoundLabel.setText(_translate("MainWindow", "Number of Results:"))

    def bind_buttons(self):
        self.Refresh.clicked.connect(self.refresh_data)
        self.Export.clicked.connect(self.export_data)

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
        self.refresh_elements()

    def refresh_elements(self):
        if self.filtered:
            self.results_model = PandasModel(self.edited_data_frame)
            self.results_model = PandasModel(self.edited_data_frame)
            self.DevicesTable.setModel(self.results_model)
        else:
            self.results_model = PandasModel(self.data_frame)
            self.results_model = PandasModel(self.data_frame)
            self.DevicesTable.setModel(self.results_model)
        self.DevicesTable.create()
        self.NumFoundLabel.setText("Number of Results:  " + str(self.response.active_results))

    def export_data(self):
        self.data_handler.print_to_csv(self.data_frame)

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