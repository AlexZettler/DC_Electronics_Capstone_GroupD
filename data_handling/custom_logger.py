import logging
import os
import os.path as path
from time import sleep
import datetime
import csv
import data_handling.data_retrieval


csv_formatter = logging.Formatter(
    fmt="%(asctime)s, %(levelname)s, %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

cons_formatter = logging.Formatter(
    fmt="%(asctime)s:%(levelname)s:%(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

base_directory = f"./log/"

log_directories = {
    "measurements": f"{base_directory}/measurements/",
    "outputs": f"{base_directory}/outputs/",
    "system": f"{base_directory}/"
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

    td = datetime.timedelta(minutes=1, seconds=0)
    print(f"Printing data logged in the last {td}:")

    data = data_handling.data_retrieval.iget_data_from_time_delta(file_name=file_name, time_delta=td)
    f_data = '\n'.join([f"{time}: {value}"for time,value in data])
    print(f"Data is as follows:\n{f_data}")

