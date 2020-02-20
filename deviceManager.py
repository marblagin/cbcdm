import json
import os
import sys
import logging
import requests
from PyQt5 import QtWidgets, uic

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

    def __init__(self, api_key, api_id, org_key, prod=0):

        self.api_key = api_key
        self.api_id = api_id
        self.org_key = org_key
        self.api_auth = self.api_key + "/" + self.api_id
        self.api_headers = {'Content-Type': 'application/json', 'X-Auth-Token': self.api_auth}
        logger.debug("Header set to " + str(self.api_headers))
        prod_switch = {
            0: "https://api.confer.net",
            5: "https://defense-prod05.conferdeploy.net",
            6: "https://defense-eu.conferdeploy.net"
        }

        self.api_device_url = prod_switch[prod] + "/appservices/v6/orgs/" + self.org_key + "/devices/_search"
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
            file.write(json.dumps(data_input, file, indent=4))

        logger.debug("Data dumped to file")

    def read_data(self):

        if os.path.exists(self.data_location):

            with open(self.data_location, "r") as file:
                return json.loads(file.read())
        else:
            logger.error("File not found", level=3)


class Device:

    def __init__(self, device_data, counter_reference):
        self.name = device_data["results"][counter_reference]["name"]
        self.status = device_data["results"][counter_reference]["status"]
        self.device_id = device_data["results"][counter_reference]["id"]
        if device_data["results"][counter_reference]["uninstall_code"] is None:
            self.uninstall_code = "Not Found"
        else:
            self.uninstall_code = device_data["results"][counter_reference]["uninstall_code"]


class Ui(QtWidgets.QWidget):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("cbcdm.ui", self)
        self.show()


def main():
    new_request = ApiRequest("BT8AD1M6GK6TLPC6NSJDZ3SH", "K2R11QCZ71", "79ZAMKRN", prod=6)
    if new_request.success:
        new_data_handler = DataHandler(data_file="devices.json")
        new_data_handler.file_dump(new_request.api_response.content)
        new_request.api_response.print_devices()
    app = QtWidgets.QWidget(sys.argv)
    window = Ui()
    app.exec_()


if __name__ == "__main__":
    sys.exit(main())
