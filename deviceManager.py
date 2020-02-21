import configparser
import json
import os
import sys
import logging
import requests
from PyQt5 import uic, QtWidgets, QtCore, QtGui

logger = logging.getLogger("cbcdm")
logger.setLevel(logging.DEBUG)
lf = logging.FileHandler("cbcdm.log")
lf.setLevel(logging.DEBUG)
lh = logging.StreamHandler()
lh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
lf.setFormatter(formatter)
lh.setFormatter(formatter)
logger.addHandler(lf)
logger.addHandler(lh)
logger.debug("Logging Initialized")


class ApiRequest:

    def __init__(self, api_auth, org_key, api_url, ssl=False):

        self.org_key = org_key
        self.api_auth = api_auth
        self.api_headers = {'Content-Type': 'application/json', 'X-Auth-Token': self.api_auth}
        logger.debug("Header set to " + str(self.api_headers))
        # Todo implement ssl verification
        self.api_device_url = api_url + "/appservices/v6/orgs/" + self.org_key + "/devices/_search"
        logger.debug("Prod URL set to " + self.api_device_url)

        self.request_payload = "{\n    \"criteria\": {\n        \"status\": [\n            \"ALL\"\n        ]\n    }\n}"

        response = requests.request("POST", self.api_device_url, data=self.request_payload, headers=self.api_headers)

        logger.debug("HTTP request sent")
        if response:

            logger.debug("HTTP response received")
            self.api_response = Response(response.json())
            self.success = True
        else:

            logger.error("HTTP Error in API Request, Status Code: " + str(response.status_code))
            self.success = False


class Response:

    def __init__(self, response_data):
        self.content = response_data
        self.total_results = response_data["num_found"]
        logger.debug("Number of devices found: " + str(self.total_results))

        self.all_devices = []
        counter = 0

        while counter < self.total_results:
            new_device = Device(self.content, counter)
            self.all_devices.append(new_device)
            counter += 1

    def print_devices(self):
        for x in range(len(self.all_devices)):
            print(self.all_devices[x].name)
            print(self.all_devices[x].uninstall_code)

    def get_text_response(self):
        return self.content.text


class DataHandler:

    def __init__(self, data_path="data", data_file="data_file.json"):

        self.data_path = data_path
        self.data_file = data_file
        self.data_location = data_path + "/" + data_file

    def file_dump(self, data_input):

        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)

        with open(self.data_location, "w") as file:
            file.write(json.dumps(data_input, indent=4))

        logger.debug("Data dumped to file")

    def read_data(self):

        if os.path.exists(self.data_location):

            with open(self.data_location, "r") as file:
                return json.loads(file.read())
        else:
            logger.error("File not found")


class Auth:

    def __init__(self, auth_path="config", auth_file="credentials.ini"):
        self.auth_file = auth_file
        self.auth_path = auth_path
        self.auth_location = self.auth_path + "/" + self.auth_file
        config = configparser.ConfigParser()
        if not os.path.exists(self.auth_location):
            logger.warning("Credential File not found, creating a new one")
            # Todo need to ask for input to create api token for ini file
            # Todo setup default profiles for each prod
            config['default'] = {
                'url': 'https://api-prod06.conferdeploy.net',
                'token': 'AAAAAAAAAAAAA/BBBBB',
                'org_key': 'CCCCC'
            }
            with open(self.auth_location, 'w') as configfile:
                config.write(configfile)
        config.read(self.auth_location)
        logger.debug("Config file now loaded")
        self.api_url = config['default']['url']
        self.api_token = config['default']['token']
        self.org_key = config['default']['org_key']
        self.ssl = config['default']['ssl_verify']

    # Todo need code to return and set profile for API
    def return_profile(self):
        return "default"

class Device:

    def __init__(self, device_data, counter_reference):
        self.name = device_data["results"][counter_reference]["name"]
        self.status = device_data["results"][counter_reference]["status"]
        self.device_id = device_data["results"][counter_reference]["id"]
        if device_data["results"][counter_reference]["uninstall_code"] is None:
            self.uninstall_code = "Not Found"
        else:
            self.uninstall_code = device_data["results"][counter_reference]["uninstall_code"]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, api_config):
        super(MainWindow, self).__init__()
        uic.loadUi('cbcdm.ui', self)
        self.setWindowTitle("CBCDM")
        self.resize(930, 640)

        self.DevicesTable = QtWidgets.QTableView(self)
        self.DevicesTable.setGeometry(QtCore.QRect(20, 110, 731, 481))
        self.DevicesTable.setToolTipDuration(0)
        self.DevicesTable.setObjectName("DevicesTable")

        self.Refresh = QtWidgets.QPushButton(self)
        self.Refresh.setGeometry(QtCore.QRect(150, 600, 89, 25))
        self.Refresh.setObjectName("Refresh")
        self.Refresh.setText("Refresh")
        self.Refresh.clicked.connect(self.refresh_button_pressed)

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
        # Todo not able to set the current text of the combo box, need to fix
        self.APIComboBox.setCurrentText(api_config.return_profile())
        self.APIComboBox.setObjectName("APIComboBox")

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

    def refresh_button_pressed(self):
        logger.debug('Refresh button pressed')

    # Todo: need to create all the widgets functions


def main():
    new_auth = Auth()
    new_request = ApiRequest(new_auth.api_token, new_auth.org_key, new_auth.api_url)
    if new_request.success:
        new_data_handler = DataHandler(data_file="devices.json")
        new_data_handler.file_dump(new_request.api_response.content)
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(new_auth)
    window.show()
    app.exec_()


if __name__ == "__main__":
    sys.exit(main())
