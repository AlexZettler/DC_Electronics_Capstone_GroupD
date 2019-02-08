import logging
import os
import os.path as path
import glob

csv_formatter = logging.Formatter(
    fmt="%(asctime)s,%(levelname)s,%{message}s,",
    datefmt='%Y-%m-%d %H:%M:%S'
)

cons_formatter = logging.Formatter(
    fmt="%(asctime)s:%(levelname)s:%{message}s",
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

    file_name = os.path.join(log_directories["measurements"],"system.csv")
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


def iget_log_dirs():
    for item in os.listdir(base_directory):
        if os.path.isdir(base_directory):
            yield item


def iget_device_files_from_log_directory(dir):

    for item in os.listdir(dir):
        if os.path.isfile(dir) and (item.split(".")[-1] == "csv"):
            yield item


#create_path_for_file("./lol/lol.txt")