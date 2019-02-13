import random
import custom_logger

def get_device_types(self):
    return custom_logger.log_directories.keys()

def get_device_files_of_type(self, device_type):
    return custom_logger.iget_device_files_from_log_directory(device_type)

def get_rand_data():
    return [[random.random() for i in range(25)]for i in range(5)]

#print(self.get_devices_from_log_directory("../log"))