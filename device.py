import logging


class Device:

    def __init__(self, device_data, counter_reference):
        logging.debug('Creating new device, ID: ' + str(device_data["results"][counter_reference]["id"]))
        self.name = device_data["results"][counter_reference]["name"]
        self.status = device_data["results"][counter_reference]["status"]
        self.device_id = device_data["results"][counter_reference]["id"]
        if device_data["results"][counter_reference]["uninstall_code"] is None:
            self.uninstall_code = "Not Found"
        else:
            self.uninstall_code = device_data["results"][counter_reference]["uninstall_code"]