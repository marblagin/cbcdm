import logging

from PyQt5.QtWidgets import QMessageBox

from api import ApiRequest, Response, Auth
from config import AuthConfig, Log
from data import DataHandler
from PyQt5 import uic, QtWidgets, QtCore
from pandas import DataFrame


class MainWindow(QtWidgets.QFrame):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi('ui/cbcdmv1.2.ui', self)
        self.setWindowTitle("CBCDM")

        # Initializes UI objects
        self.DevicesTable = QtWidgets.QTableView(self)
        self.DevicesTable.setGeometry(QtCore.QRect(20, 100, 991, 701))
        self.DevicesTable.setProperty("toolTipDuration", 0)
        self.DevicesTable.setObjectName("DevicesTable")
        self.Refresh = QtWidgets.QPushButton(self)
        self.Refresh.setGeometry(QtCore.QRect(370, 20, 141, 61))
        self.Refresh.setObjectName("Refresh")
        self.Export = QtWidgets.QPushButton(self)
        self.Export.setGeometry(QtCore.QRect(520, 20, 141, 61))
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
        self.ColumnList.setGeometry(QtCore.QRect(1020, 130, 256, 671))
        self.ColumnList.setObjectName("ColumnList")
        self.NumFoundLabel = QtWidgets.QLabel(self)
        self.NumFoundLabel.setGeometry(QtCore.QRect(680, 10, 221, 21))
        self.NumFoundLabel.setObjectName("NumFoundLabel")
        self.SelectAll = QtWidgets.QPushButton(self)
        self.SelectAll.setGeometry(QtCore.QRect(1020, 100, 131, 27))
        self.SelectAll.setObjectName("SelectAll")
        self.DeslectAll = QtWidgets.QPushButton(self)
        self.DeslectAll.setGeometry(QtCore.QRect(1154, 100, 121, 27))
        self.DeslectAll.setObjectName("DeslectAll")
        self.ActiveNum = QtWidgets.QLabel(self)
        self.ActiveNum.setGeometry(QtCore.QRect(680, 40, 211, 17))
        self.ActiveNum.setObjectName("ActiveNum")
        self.deregNum = QtWidgets.QLabel(self)
        self.deregNum.setGeometry(QtCore.QRect(680, 70, 221, 17))
        self.deregNum.setObjectName("deregNum")

        QtCore.QMetaObject.connectSlotsByName(self)

        # Data Request and Load
        Log()
        self.auth_config = AuthConfig()
        if self.auth_config.first_setup:
            # Todo need to ask for input to create api token for ini file
            self.auth_config.create_profile("Default", "URL", "Token", "Key", "Org Key")
        self.auth = Auth(self.auth_config.config, self.auth_config.profiles[0])
        self.request = ApiRequest(self.auth)
        self.response = Response(self.request.http_request())
        if self.request.success:
            self.data_handler = DataHandler(data_file="devices.json", data_path="data")
            if self.data_handler.file_dump(self.response.content):
                self.data_frame = DataFrame(self.data_handler.read_json_data_results())
                self.data_frame_columns = []
                for col in self.data_frame.columns:
                    self.data_frame_columns.append(col)
                self.edited_data_frame = self.data_frame
                self.results_model = PandasModel(self.data_frame)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            msg.setText("This is a message box")
            msg.setInformativeText("This is additional information")
            msg.setWindowTitle("MessageBox demo")
            msg.setDetailedText("The details are as follows:")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        # Environment Variables
        self.filtered = False

        # Assign data to UI elements
        self.retranslateUi(self)
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
        counter = 0
        for x in self.data_frame_columns:
            item = QtWidgets.QListWidgetItem()
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked)
            item.setText(str(x))
            self.ColumnList.addItem(item)
            counter += 1
        self.ColumnList.setSortingEnabled(__sortingEnabled)
        self.ColumnList.sortItems(QtCore.Qt.AscendingOrder)
        self.NumFoundLabel.setText(_translate("MainWindow", "Number of Results:"))
        self.NumFoundLabel.setText(_translate("MainWindow", "Number of Results:"))
        self.SelectAll.setText(_translate("MainWindow", "Select All"))
        self.DeslectAll.setText(_translate("MainWindow", "Deselect All"))
        self.ActiveNum.setText(_translate("MainWindow", "Registered Devices:"))
        self.deregNum.setText(_translate("MainWindow", "Deregistered Devices: "))

    def bind_buttons(self):
        self.Refresh.clicked.connect(self.refresh_data)
        self.Export.clicked.connect(self.export_data)
        self.SelectAll.clicked.connect(self.select_all)
        self.DeslectAll.clicked.connect(self.deselect_all)

    def refresh_data(self):
        logging.info('Refreshing data')
        logging.debug('ComboBox Set to index ' + str(self.APIComboBox.currentIndex()))
        logging.debug('Profile selected: ' + self.APIComboBox.itemText(self.APIComboBox.currentIndex()))
        self.request = ApiRequest(
            self.auth_config.load_profile(self.APIComboBox.itemText(self.APIComboBox.currentIndex())))
        self.response = Response(self.request.http_request())

        # Todo Consider removing the constant data dumping
        if self.request.success:
            if self.data_handler.file_dump(self.response.content):
                self.data_frame = DataFrame(self.data_handler.read_json_data_results())
                self.data_frame_columns = []
                for col in self.data_frame.columns:
                    self.data_frame_columns.append(col)
                self.edited_data_frame = self.data_frame
            self.refresh_elements()

    def refresh_elements(self):
        for x in range(self.ColumnList.__len__()):
            if not self.ColumnList.item(x).checkState():
                logging.info("Data is now filtered")
                self.filtered = True
                break
            else:
                self.filtered = False
        if self.filtered:
            self.edited_data_frame = self.filter_data(self.data_frame)
            logging.info("Setting table with filtered data")
            self.results_model = PandasModel(self.edited_data_frame)
            self.DevicesTable.setModel(self.results_model)
        else:
            logging.info("Setting table with default data")
            self.results_model = PandasModel(self.data_frame)
            self.DevicesTable.setModel(self.results_model)
        self.DevicesTable.create()
        self.NumFoundLabel.setText("Number of Results:  " + str(self.response.total_results))
        self.ActiveNum.setText("Registered Devices:  " + str(self.response.active_results))
        self.deregNum.setText("Deregistered Devices:  " + str(self.response.num_deregistered))

    def filter_data(self, data_frame):
        for x in range(self.ColumnList.__len__()):
            if not self.ColumnList.item(x).checkState():
                try:
                    data_frame = data_frame.drop(columns=self.ColumnList.item(x).text())
                except KeyError:
                    logging.warning("Could not find column " + self.ColumnList.item(x).text())
                    continue
        return data_frame

    def export_data(self):
        if self.filtered:
            self.data_handler.print_to_csv(self.edited_data_frame)
        else:
            self.data_handler.print_to_csv(self.data_frame)

    def select_all(self):
        for x in range(self.ColumnList.__len__()):
            self.ColumnList.item(x).setCheckState(QtCore.Qt.Checked)

    def deselect_all(self):
        for x in range(self.ColumnList.__len__()):
            self.ColumnList.item(x).setCheckState(QtCore.Qt.Unchecked)


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

# Todo add option to save filtered view
# Todo add header to table showing all devices
# Todo figure out why some machines are not appearing in the results (linux machines for instance)
