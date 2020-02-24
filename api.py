import configparser
import os
import requests
import logging
from device import Device


class ApiRequest:

    def __init__(self, profile='default'):
        self.auth_profile = profile
        self.auth = Auth(self.auth_profile)
        self.success = False
        self.api_headers = {'Content-Type': 'application/json', 'X-Auth-Token': self.auth.api_token}
        logging.debug("Header set to " + str(self.api_headers))
        # Todo implement ssl verification
        self.api_device_url = self.auth.api_url + "/appservices/v6/orgs/" + self.auth.org_key + "/devices/_search"
        logging.debug("Prod URL set to " + self.api_device_url)

    def http_request(self, payload=None):

        if payload is None:

            request_payload = "{\n    \"criteria\": {\n        \"status\": [\n            \"ALL\"\n        ]\n    }\n}"

        else:

            request_payload = payload

        response = requests.request("POST", self.api_device_url, data=request_payload, headers=self.api_headers)

        logging.info("HTTP request sent")
        if response:

            logging.info("HTTP response received")
            self.success = True
            return response.json()

        else:

            logging.error("HTTP Error in API Request, Status Code: " + str(response.status_code))


class Response:

    def __init__(self, response_data):
        self.content = response_data
        self.total_results = response_data["num_found"]
        logging.debug("Number of devices found: " + str(self.total_results))

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


class Auth:

    def __init__(self, profile, auth_path="config", auth_file="credentials.ini"):

        self.auth_file = auth_file
        self.auth_path = auth_path
        self.auth_location = self.auth_path + "/" + self.auth_file
        config = configparser.ConfigParser()

        if not os.path.exists(self.auth_location):
            logging.warning("Credential File not found, creating a new one")
            # Todo need to ask for input to create api token for ini file
            config['default'] = {
                'url': 'https://api-prod06.conferdeploy.net',
                'token': 'AAAAAAAAAAAAA/BBBBB',
                'org_key': 'CCCCC'
            }
            with open(self.auth_location, 'w') as configfile:
                config.write(configfile)

        config.read(self.auth_location)
        logging.info("Config file now loaded")
        self.profiles = config.sections()
        logging.debug(str(config.sections()) + " profile/s loaded")
        self.api_url = config[profile]['url']
        self.api_token = config[profile]['token']
        self.org_key = config[profile]['org_key']
        self.ssl = config[profile]['ssl_verify']

    def get_num_profiles(self):
        return len(self.profiles)
    # Todo need code to return and set profile for API
