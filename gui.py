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

class Ui_MainWindow(object):
    def __init__(self, MainWindow):

        # uic.loadUi('ui/cbcdmv1.3.ui', MainWindow)

        # Initializes UI objects
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 834)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.NumFoundLabel = QtWidgets.QLabel(self.centralwidget)
        self.NumFoundLabel.setGeometry(QtCore.QRect(770, 110, 221, 21))
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
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 110, 201, 17))
        self.label.setObjectName("label")
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
        MainWindow.setCentralWidget(self.centralwidget)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Data Request and Load
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
        self.retranslateUi(MainWindow)
        self.refresh_elements()
        logging.debug('Number of profiles to load: ' + str(self.auth_config.get_num_profiles()))
        self.add_api_config()
        self.bind_buttons()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.NumFoundLabel.setText(_translate("MainWindow", "Number of Results:"))
        self.Refresh.setText(_translate("MainWindow", "Refresh"))
        self.SelectAll.setText(_translate("MainWindow", "Select All"))
        self.DeselectAll.setText(_translate("MainWindow", "Deselect All"))
        self.label.setText(_translate("MainWindow", "Registered Devices: 0"))
        self.Export.setText(_translate("MainWindow", "Export to CSV"))
        self.APITitle.setText(_translate("MainWindow", "Select API:"))
        self.AddAPI.setText(_translate("MainWindow", "Add API"))

        self.set_up_items()

    def set_up_items(self):
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

class Ui_APIDialog(object):
    def __init__(self, APIDialog):
        APIDialog.setObjectName("APIDialog")
        APIDialog.resize(333, 400)
        self.DialogButton = QtWidgets.QDialogButtonBox(APIDialog)
        self.DialogButton.setGeometry(QtCore.QRect(130, 350, 181, 32))
        self.DialogButton.setOrientation(QtCore.Qt.Horizontal)
        self.DialogButton.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.DialogButton.setObjectName("DialogButton")
        self.APICombo = QtWidgets.QComboBox(APIDialog)
        self.APICombo.setGeometry(QtCore.QRect(20, 100, 291, 27))
        self.APICombo.setObjectName("APICombo")
        self.TokenLine = QtWidgets.QLineEdit(APIDialog)
        self.TokenLine.setGeometry(QtCore.QRect(20, 160, 291, 29))
        self.TokenLine.setObjectName("TokenLine")
        self.OrgLine = QtWidgets.QLineEdit(APIDialog)
        self.OrgLine.setGeometry(QtCore.QRect(20, 300, 291, 29))
        self.OrgLine.setObjectName("OrgLine")
        self.APIURLLabel = QtWidgets.QLabel(APIDialog)
        self.APIURLLabel.setGeometry(QtCore.QRect(20, 80, 66, 17))
        self.APIURLLabel.setObjectName("APIURLLabel")
        self.TokenLabel = QtWidgets.QLabel(APIDialog)
        self.TokenLabel.setGeometry(QtCore.QRect(20, 140, 91, 17))
        self.TokenLabel.setObjectName("TokenLabel")
        self.OrgLabel = QtWidgets.QLabel(APIDialog)
        self.OrgLabel.setGeometry(QtCore.QRect(20, 280, 121, 17))
        self.OrgLabel.setObjectName("OrgLabel")
        self.CredLabel = QtWidgets.QLabel(APIDialog)
        self.CredLabel.setGeometry(QtCore.QRect(20, 20, 161, 17))
        self.CredLabel.setObjectName("CredLabel")
        self.CredLine = QtWidgets.QLineEdit(APIDialog)
        self.CredLine.setGeometry(QtCore.QRect(20, 40, 291, 29))
        self.CredLine.setText("")
        self.CredLine.setObjectName("CredLine")
        self.KeyLabel = QtWidgets.QLabel(APIDialog)
        self.KeyLabel.setGeometry(QtCore.QRect(20, 200, 66, 17))
        self.KeyLabel.setObjectName("KeyLabel")
        self.KeyLine = QtWidgets.QLineEdit(APIDialog)
        self.KeyLine.setGeometry(QtCore.QRect(20, 230, 291, 29))
        self.KeyLine.setObjectName("KeyLine")

        self.retranslateUi(APIDialog)
        self.DialogButton.accepted.connect(APIDialog.accept)
        self.DialogButton.rejected.connect(APIDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(APIDialog)

    def retranslateUi(self, APIDialog):
        _translate = QtCore.QCoreApplication.translate
        APIDialog.setWindowTitle(_translate("APIDialog", "Dialog"))
        self.APIURLLabel.setText(_translate("APIDialog", "API URL:"))
        self.TokenLabel.setText(_translate("APIDialog", "API Token:"))
        self.OrgLabel.setText(_translate("APIDialog", "API Org Key:"))
        self.CredLabel.setText(_translate("APIDialog", "Credential Set Name:"))
        self.KeyLabel.setText(_translate("APIDialog", "API Key:"))

class GUI:
    def __init__(self):
        self.Ui_MainWindow = Ui_MainWindow(QtWidgets.QMainWindow())
        self.Ui_MainWindow.show()


# Todo add option to save filtered view
# Todo add header to table showing all devices
# Todo figure out why some machines are not appearing in the results (linux machines for instance)
