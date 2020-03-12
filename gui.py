import logging
from PyQt5.QtWidgets import QMessageBox
from api import ApiRequest, Response, Auth
from config import AuthConfig
from data import DataHandler
from PyQt5 import uic, QtWidgets, QtCore
from pandas import DataFrame


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


class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        uic.loadUi('ui/cbcdmv1.4.ui', self)

        # Initializes UI objects
        self.setObjectName("MainWindow")
        self.resize(1280, 834)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.NumFoundLabel = QtWidgets.QLabel(self.centralwidget)
        self.NumFoundLabel.setGeometry(QtCore.QRect(10, 110, 201, 17))
        self.NumFoundLabel.setObjectName("NumFoundLabel")
        self.DevicesTable = QtWidgets.QTableView(self.centralwidget)
        self.DevicesTable.setGeometry(QtCore.QRect(10, 140, 991, 661))
        self.DevicesTable.setProperty("toolTipDuration", 0)
        self.DevicesTable.setObjectName("DevicesTable")
        self.Refresh = QtWidgets.QPushButton(self.centralwidget)
        self.Refresh.setGeometry(QtCore.QRect(360, 20, 141, 61))
        self.Refresh.setObjectName("Refresh")
        self.ColumnList = QtWidgets.QListWidget(self.centralwidget)
        self.ColumnList.setGeometry(QtCore.QRect(1010, 140, 256, 661))
        self.ColumnList.setObjectName("ColumnList")
        self.SelectAll = QtWidgets.QPushButton(self.centralwidget)
        self.SelectAll.setGeometry(QtCore.QRect(1010, 110, 131, 27))
        self.SelectAll.setObjectName("SelectAll")
        self.DeselectAll = QtWidgets.QPushButton(self.centralwidget)
        self.DeselectAll.setGeometry(QtCore.QRect(1144, 110, 121, 27))
        self.DeselectAll.setObjectName("DeslectAll")
        self.Export = QtWidgets.QPushButton(self.centralwidget)
        self.Export.setGeometry(QtCore.QRect(510, 20, 141, 61))
        self.Export.setObjectName("Export")
        self.APIFrame = QtWidgets.QFrame(self.centralwidget)
        self.APIFrame.setGeometry(QtCore.QRect(10, 10, 341, 81))
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
        self.AddAPI = QtWidgets.QPushButton(self.centralwidget)
        self.AddAPI.setGeometry(QtCore.QRect(660, 20, 141, 61))
        self.AddAPI.setObjectName("AddAPIBtn")
        self.setCentralWidget(self.centralwidget)

        QtCore.QMetaObject.connectSlotsByName(self)

        # Initialise other frames
        self.api_info_dialog = Ui_APIDialog()

        # Data Request and Load
        self.auth_config = AuthConfig()
        if self.auth_config.first_setup:
            self.api_info_dialog.show()
            self.auth_config.create_profile(self.api_info_dialog.CredLine.text(), self.api_info_dialog.APICombo.itemText(0),
                                            self.api_info_dialog.TokenLine.text(), self.api_info_dialog.KeyLine.text(),
                                            self.api_info_dialog.OrgLine.text(), "True")
        self.auth_config.load_config()
        logging.debug('Number of profiles to load: ' + str(self.auth_config.get_num_profiles()))
        self.add_api_config()

        self.auth = Auth(self.auth_config.config, self.auth_config.profiles[0])
        self.data_handler = DataHandler(data_file="devices.json", data_path="data")

        # Environment Variables
        self.filtered = False

        self.request = ApiRequest(self.auth)
        self.request.http_request()
        if self.request.success:
            self.response = Response(self.request.json_response)
            if self.data_handler.file_dump(self.response.content):
                self.data_frame = DataFrame(self.data_handler.read_json_data_results())
                self.data_frame_columns = []
                for col in self.data_frame.columns:
                    self.data_frame_columns.append(col)
                self.edited_data_frame = self.data_frame
                self.results_model = PandasModel(self.data_frame)
            self.refresh_elements()
            self.set_up_items()

        self.bind_buttons()
        self.retranslateUi(self)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.NumFoundLabel.setText(_translate("MainWindow", "Number of Results:"))
        self.Refresh.setText(_translate("MainWindow", "Refresh"))
        self.SelectAll.setText(_translate("MainWindow", "Select All"))
        self.DeselectAll.setText(_translate("MainWindow", "Deselect All"))
        self.Export.setText(_translate("MainWindow", "Export to CSV"))
        self.APITitle.setText(_translate("MainWindow", "Select API:"))
        self.AddAPI.setText(_translate("MainWindow", "Add API"))

    def set_up_items(self):
        self.ColumnList = QtWidgets.QListWidget(self.centralwidget)
        self.ColumnList.setGeometry(QtCore.QRect(1010, 140, 256, 661))
        self.ColumnList.setObjectName("ColumnList")
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

    def add_api_config(self):
        for x in range(self.auth_config.get_num_profiles()):
            self.APIComboBox.addItem(self.auth_config.profiles[x])
            logging.debug('Adding profile ' + str(self.auth_config.profiles[x]) + ' to combo box')

    def bind_buttons(self):
        self.Refresh.clicked.connect(self.refresh_data)
        self.Export.clicked.connect(self.export_data)
        self.SelectAll.clicked.connect(self.select_all)
        self.DeselectAll.clicked.connect(self.deselect_all)
        self.AddAPI.clicked.connect(self.add_api)

    def refresh_data(self):
        logging.info('Refreshing data')
        logging.debug('ComboBox Set to index ' + str(self.APIComboBox.currentIndex()))
        logging.debug('Profile selected: ' + self.APIComboBox.itemText(self.APIComboBox.currentIndex()))
        self.request = ApiRequest(
            self.auth_config.load_profile(self.APIComboBox.itemText(self.APIComboBox.currentIndex())))

        # Todo Consider removing the constant data dumping
        self.request.http_request()
        if self.request.success:
            self.response = Response(self.request.json_response)
            if self.data_handler.file_dump(self.response.content):
                self.data_frame = DataFrame(self.data_handler.read_json_data_results())
                self.data_frame_columns = []
                for col in self.data_frame.columns:
                    self.data_frame_columns.append(col)
                self.edited_data_frame = self.data_frame
            self.refresh_elements()
            self.set_up_items()
        else:
            QMessageBox.about(self, "Failed Request", "Failed to Pull Data from API, Error code:"
                              + str(self.request.response_code))

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
        self.NumFoundLabel.setText("Number of Results:  " + str(self.response.active_results))

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
        QMessageBox.about(self, "Export Data", "Data has been exported to CSV")

    def select_all(self):
        for x in range(self.ColumnList.__len__()):
            self.ColumnList.item(x).setCheckState(QtCore.Qt.Checked)

    def deselect_all(self):
        for x in range(self.ColumnList.__len__()):
            self.ColumnList.item(x).setCheckState(QtCore.Qt.Unchecked)

    def add_api(self):
        logging.info("Adding new API")
        self.api_info_dialog.show()


class Ui_APIDialog(QtWidgets.QDialog):
    def __init__(self):
        super(Ui_APIDialog, self).__init__()
        self.setObjectName("APIDialog")
        self.resize(333, 400)
        self.DialogButton = QtWidgets.QDialogButtonBox(self)
        self.DialogButton.setGeometry(QtCore.QRect(130, 350, 181, 32))
        self.DialogButton.setOrientation(QtCore.Qt.Horizontal)
        self.DialogButton.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.DialogButton.setObjectName("DialogButton")
        self.APICombo = QtWidgets.QComboBox(self)
        self.APICombo.setGeometry(QtCore.QRect(20, 100, 291, 27))
        self.APICombo.setObjectName("APICombo")
        self.TokenLine = QtWidgets.QLineEdit(self)
        self.TokenLine.setGeometry(QtCore.QRect(20, 160, 291, 29))
        self.TokenLine.setObjectName("TokenLine")
        self.OrgLine = QtWidgets.QLineEdit(self)
        self.OrgLine.setGeometry(QtCore.QRect(20, 300, 291, 29))
        self.OrgLine.setObjectName("OrgLine")
        self.APIURLLabel = QtWidgets.QLabel(self)
        self.APIURLLabel.setGeometry(QtCore.QRect(20, 80, 66, 17))
        self.APIURLLabel.setObjectName("APIURLLabel")
        self.TokenLabel = QtWidgets.QLabel(self)
        self.TokenLabel.setGeometry(QtCore.QRect(20, 140, 91, 17))
        self.TokenLabel.setObjectName("TokenLabel")
        self.OrgLabel = QtWidgets.QLabel(self)
        self.OrgLabel.setGeometry(QtCore.QRect(20, 280, 121, 17))
        self.OrgLabel.setObjectName("OrgLabel")
        self.CredLabel = QtWidgets.QLabel(self)
        self.CredLabel.setGeometry(QtCore.QRect(20, 20, 161, 17))
        self.CredLabel.setObjectName("CredLabel")
        self.CredLine = QtWidgets.QLineEdit(self)
        self.CredLine.setGeometry(QtCore.QRect(20, 40, 291, 29))
        self.CredLine.setText("")
        self.CredLine.setObjectName("CredLine")
        self.KeyLabel = QtWidgets.QLabel(self)
        self.KeyLabel.setGeometry(QtCore.QRect(20, 200, 66, 17))
        self.KeyLabel.setObjectName("KeyLabel")
        self.KeyLine = QtWidgets.QLineEdit(self)
        self.KeyLine.setGeometry(QtCore.QRect(20, 230, 291, 29))
        self.KeyLine.setObjectName("KeyLine")

        self.retranslateUi(self)
        self.DialogButton.accepted.connect(self.parse_api)
        self.DialogButton.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.APICombo.addItem("https://defense-eu.conferdeploy.net")
        self.APICombo.addItem("https://defense-prod05.conferdeploy.net")

        # API Values
        self.cred = ""
        self.token = ""
        self.url = ""
        self.org = ""
        self.key = ""

    def retranslateUi(self, APIDialog):
        _translate = QtCore.QCoreApplication.translate
        APIDialog.setWindowTitle(_translate("APIDialog", "Dialog"))
        self.APIURLLabel.setText(_translate("APIDialog", "API URL:"))
        self.TokenLabel.setText(_translate("APIDialog", "API Token:"))
        self.OrgLabel.setText(_translate("APIDialog", "API Org Key:"))
        self.CredLabel.setText(_translate("APIDialog", "Credential Set Name:"))
        self.KeyLabel.setText(_translate("APIDialog", "API Key:"))

    def parse_api(self):
        logging.debug("Gathering info from entered API details")
        # Todo Flesh out the input validation here
        self.cred = self.CredLine.text()
        self.token = self.TokenLine.text()
        self.url = self.APICombo.itemText(self.APICombo.currentIndex())
        self.org = self.OrgLine.text()
        self.key = self.KeyLine.text()
        self.close()


# Todo add option to save filtered view
# Todo figure out why some machines are not appearing in the results (linux machines for instance)
