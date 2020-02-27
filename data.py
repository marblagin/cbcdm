import json
import os
import logging
import pandas


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

        logging.info("Data dumped to file")

    def read_json_data_results(self):

        if os.path.exists(self.data_location):

            with open(self.data_location, "r") as file:
                data = json.loads(file.read())
                logging.info("json file loaded")
                out = data['results']
                return out
        else:
            logging.error("File not found")


# Todo create function to export (filtered) devices to CSV/Text
