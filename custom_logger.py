import logging
import os
import os.path as path

csv_formatter = logging.Formatter(
    fmt="%(asctime)s,%(levelname)s,%{message}s,",
    datefmt='%Y-%m-%d %H:%M:%S'
)

cons_formatter = logging.Formatter(
    fmt="%(asctime)s:%(levelname)s:%{message}s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

def create_measurement_logger(device_id):
    logger = logging.getLogger(f"measurement-{device_id}")
    logger.setLevel(logging.INFO)

    file_name = f"./log/measurements/{device_id}.csv"
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

    file_name = f"./log/outputs/{device_id}.csv"
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

    file_name = "./log/system.csv"
    create_path_for_file(file_name)

    f_handler = logging.FileHandler(file_name)
    f_handler.setFormatter(csv_formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(cons_formatter)
    logger.addHandler(s_handler)

    return logger


def create_path_for_file(file):
    file_path = os.path.basename(file)
    dir_path = path.dirname(file_path)
    print(dir_path)

    if not path.exists(dir_path):
        os.makedirs(dir_path)

create_path_for_file("./lol/lol.txt")