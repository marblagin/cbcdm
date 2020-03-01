import json
import os
import logging
from pandas import DataFrame


class DataHandler:

    def __init__(self, data_path="data", data_file="data_file.json", export_path="export", export_file="api_export"):

        self.data_path = data_path
        self.data_file = data_file
        self.data_location = data_path + "/" + data_file
        self.export_path = export_path
        self.export_file = export_file
        self.export_data_location = export_path + "/" + export_file

    def file_dump(self, data_input):

        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)

        try:
            with open(self.data_location, "w") as file:
                file.write(json.dumps(data_input, indent=4))

            logging.info("Data dumped to file")
            return True
        except:
            logging.error("Failed to dump JSON data to file")
            return False

    def read_json_data_results(self):

        try:

            with open(self.data_location, "r") as file:
                data = json.loads(file.read())
                logging.info("json file loaded")
                out = data['results']
                return out

        except FileNotFoundError:
            logging.error("Failed to find file at location " + str(self.data_location))

    def print_to_csv(self, panda_model):

        try:
            if not os.path.exists(self.export_path):
                os.mkdir(self.export_path)

            with open(self.export_data_location, "w") as file:
                file.write(DataFrame.to_csv(panda_model))
            logging.info("Data exported to file")
        except FileExistsError:
            logging.error("Failed to write data to csv file")

