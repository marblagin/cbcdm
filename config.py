import configparser
import os
import logging
from logging.config import fileConfig
from api import Auth


class AuthConfig:
    def __init__(self, auth_path="config", auth_file="credentials.ini"):
        self.auth_location = auth_path + "/" + auth_file
        self.config = configparser.ConfigParser()
        self.first_setup = False

        if not os.path.exists(self.auth_location):
            logging.warning("Credential File not found, first time setup")
            self.first_setup = True

        self.config.read(self.auth_location)
        logging.info("Config file now loaded")
        self.profiles = self.config.sections()
        logging.debug(str(self.config.sections()) + " profile/s loaded")

    def create_profile(self, profile_name, url, token, key, org_key):
        logging.info("Creating credential profile")
        token_key = str(token) + '/' + str(key)
        self.config[profile_name] = {
            'url': url,
            'token': token_key,
            'org_key': org_key
        }
        with open(self.auth_location, 'w') as configfile:
            self.config.write(configfile)

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


class Log:
    def __init__(self):
        fileConfig("config/logging_config.ini")
        logger = logging.getLogger(__name__)
        logger.info("Logging Initialized")
