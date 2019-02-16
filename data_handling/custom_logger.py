import logging
import os
import os.path as path
from time import sleep
import datetime
import csv

from system.system_constants import base_log_directory
#from data_handling.data_retrieval import iget_data_from_time_delta


csv_formatter = logging.Formatter(
    fmt="%(asctime)s, %(levelname)s, %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

cons_formatter = logging.Formatter(
    fmt="%(asctime)s:%(levelname)s:%(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

log_directories = {
    "measurements": f"{base_log_directory}/measurements/",
    "outputs": f"{base_log_directory}/outputs/",
    "system": f"{base_log_directory}/"
}


def create_measurement_logger(device_id):
    logger = logging.getLogger(f"measurement-{device_id}")
    logger.setLevel(logging.INFO)

    print(log_directories["measurements"])

    file_name = os.path.join(log_directories["measurements"], f"{device_id}.csv")
    create_path_for_file(file_name)

    f_handler = logging.FileHandler(file_name)
    f_handler.setFormatter(csv_formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(cons_formatter)
    logger.addHandler(s_handler)

    return logger


def create_output_logger(device_id):
    logger = logging.getLogger(f"output-{device_id}")
    logger.setLevel(logging.INFO)

    file_name = os.path.join(log_directories["measurements"], f"{device_id}.csv")
    create_path_for_file(file_name)

    f_handler = logging.FileHandler(file_name)
    f_handler.setFormatter(csv_formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(cons_formatter)
    logger.addHandler(s_handler)

    return logger


def create_system_logger():
    logger = logging.getLogger("system")
    logger.setLevel(logging.INFO)

    file_name = os.path.join(log_directories["system"],"system.csv")
    create_path_for_file(file_name)

    f_handler = logging.FileHandler(file_name)
    f_handler.setFormatter(csv_formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(cons_formatter)
    logger.addHandler(s_handler)

    return logger


def create_path_for_file(file):
    abs_file_path = os.path.abspath(file)
    dir_path = '\\'.join(abs_file_path.split('\\')[0:-1])
    if not path.exists(dir_path):
        os.makedirs(dir_path)


if __name__ == "__main__":
    system_logger = create_system_logger()
    system_logger.warning("the custom logger was run as a main script")

    dummy_sensor_logger = create_measurement_logger("dummy")
    file_name = os.path.join(log_directories["measurements"], f"dummy.csv")

    for i in range(5):
        dummy_sensor_logger.info(i)