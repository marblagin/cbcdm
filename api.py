import requests
import logging


class ApiRequest:

    def __init__(self, auth_profile):
        self.auth = auth_profile
        self.success = False
        self.api_headers = {'Content-Type': 'application/json', 'X-Auth-Token': self.auth.api_token}
        logging.debug("Header set to " + str(self.api_headers))
        # Todo implement ssl verification
        self.api_device_url = self.auth.api_url + "/appservices/v6/orgs/" + self.auth.org_key + "/devices/_search"
        logging.debug("Prod URL set to " + self.api_device_url)
        self.response_code = ""

    def http_request(self, payload=None):

        if payload is None:

            request_payload = "{\n    \"criteria\": {\n        \"status\": [\n            \"ALL\"\n        ]\n    }\n}"

        else:

            request_payload = payload

        response = requests.request("POST", self.api_device_url, data=request_payload, headers=self.api_headers)
        logging.info("HTTP request sent")
        self.response_code = str(response.status_code)
        if response:

            logging.info("HTTP response received")
            self.success = True
            return response.json()

        else:

            logging.error("HTTP Error in API Request, Status Code: " + self.response_code)


class Response:

    def __init__(self, response_data):
        self.content = response_data
        self.active_results = len(response_data["results"])
        self.total_results = response_data["num_found"]
        self.num_found = response_data['num_found']
        self.num_deregistered = self.total_results - self.active_results
        logging.debug("Number of active devices found: " + str(self.active_results))
        logging.debug("Number of deregistered machines devices found: " + str(self.num_deregistered))


class Auth:

    def __init__(self, config, profile):
        self.api_url = config[profile]['url']
        self.api_token = config[profile]['token']
        self.org_key = config[profile]['org_key']
        self.ssl = config[profile]['ssl_verify']


