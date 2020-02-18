import json
import os
import sys
import logging

import requests

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
        self.api_auth = None
        self.api_headers = None
        self.set_api_header()

        prod_switch = {
            0: "https://api.confer.net",
            5: "https://api-prod05.conferdeploy.net",
            6: "https://defense-eu.conferdeploy.net/"
        }

        self.api_device_url = prod_switch[prod] + "/appservices/v6/orgs/" + self.org_key + "/devices/_search"

        self.request_payload = {
            "criteria": {
                "status": ["ALL"],
            }
        }
        self.api_response = self.http_request()

        # TODO: Configure data dump when receiving the right data for the http request
        # new_device_data = Data(data_file="devices.json")
        # new_device_data.file_dump(self.get_response())

        # TODO: Change the counter to reflect all items
        self.total_results = 5

    def set_api_header(self):

        self.api_auth = self.api_key + "/" + self.api_id
        self.api_headers = {'Content-Type': 'application/csv', 'X-Auth-Token': self.api_auth}

    def http_request(self):

        # Sends a request to the API with the set API URL and header
        session = requests.Session()
        response = session.get(self.api_device_url, data=self.request_payload, headers=self.api_headers)

        if response:

            logger.debug("API Request set and response received")
            # TODO: Fix response, its not returning the json data
            return response.request.body

        else:

            logger.error("HTTP Error in API Request, Status Code: " + str(response.status_code))

    def get_response(self):
        return self.api_response

    def get_text_response(self):
        return self.api_response

    def get_total_results(self):
        return int(self.total_results)


class Data:

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
            logger.debug("JSON File not found", level=3)


class Device:

    def __init__(self, device_data, reference):
        self.name = device_data["results"][reference]["name"]
        self.status = device_data["results"][reference]["status"]
        self.device_id = device_data["results"][reference]["deviceId"]
        self.policy_id = device_data["results"][reference]["policyId"]


def main():
    new_request = ApiRequest("BT8AD1M6GK6TLPC6NSJDZ3SH", "K2R11QCZ71", "79ZAMKRN", prod=6)

    all_devices = []
    active_devices = []

    counter = 0

    print(new_request.get_response())

# TODO: Consider removing
""""
    while counter < new_request.get_total_results():

        new_device = Device(new_request.get_response(), counter)
        all_devices.append(new_device)
        if all_devices[counter].status == "REGISTERED":
            active_devices.append(new_device)
        counter += 1

    for x in range(len(all_devices)):
        print(all_devices[x].name)
"""

if __name__ == "__main__":
    sys.exit(main())
