import configparser
import logging
import os
from api import Auth


class AuthConfig:
    def __init__(self, auth_path="config", auth_file="credentials.ini"):
        self.auth_location = auth_path + "/" + auth_file
        self.config = configparser.ConfigParser()

        if not os.path.exists(self.auth_location):
            logging.warning("Credential File not found, creating a new one")
            # Todo need to ask for input to create api token for ini file
            self.config['default'] = {
                'url': 'https://api-prod06.conferdeploy.net',
                'token': 'AAAAAAAAAAAAA/BBBBB',
                'org_key': 'CCCCC'
            }
            with open(self.auth_location, 'w') as configfile:
                self.config.write(configfile)

        self.config.read(self.auth_location)
        logging.info("Config file now loaded")
        self.profiles = self.config.sections()
        logging.debug(str(self.config.sections()) + " profile/s loaded")

    def load_profile(self, profile):
        new_auth = Auth(self.config, profile)
        return new_auth

    def get_num_profiles(self):
        return len(self.profiles)


def get_sensor_info():
    f = open('Not Used/sensorinfo.txt', 'r')
    sensor_info = f.readlines()
    new_arr = []
    for x in sensor_info:
        old = x
        new = str(old.strip('\n'))
        new_arr.append(str(new.strip('\"')))
    return new_arr
