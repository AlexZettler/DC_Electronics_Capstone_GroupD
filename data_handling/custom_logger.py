import logging
import os
import os.path as path

from system.system_constants import csv_formatter, cons_formatter, log_directories


def create_measurement_logger(device_id):
    """
    :param device_id: The sensor ID to use
    :return: A logger configured to write to the correct directory
    """

    # Create a unique logging address for the device
    logger = logging.getLogger(f"measurement-{device_id}")
    logger.setLevel(logging.INFO)


    # Define a fielpath for the measuremet logger
    file_name = os.path.join(log_directories["measurements"], f"{device_id}.csv")
    create_path_for_file(file_name)

    # Create a file formatter for the logger
    f_handler = logging.FileHandler(file_name)
    f_handler.setFormatter(csv_formatter)
    logger.addHandler(f_handler)

    # Create a stream formatter for the logger
    s_handler = logging.StreamHandler()
    s_handler.setFormatter(cons_formatter)
    logger.addHandler(s_handler)

    # Return the logger object
    return logger


def create_output_logger(device_id):
    """
    :param device_id: The output ID to use
    :return: A logger configured to write to the correct directory
    """
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
    """
    :return: A logger configured to write to the correct directory
    """
    logger = logging.getLogger("system")
    logger.setLevel(logging.INFO)

    file_name = os.path.join(log_directories["system"], "system.csv")
    create_path_for_file(file_name)

    f_handler = logging.FileHandler(file_name)
    f_handler.setFormatter(csv_formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(cons_formatter)
    logger.addHandler(s_handler)

    return logger


def create_path_for_file(file):
    """
    Creates a directory tree for the file given ensuring that the directory to create the file in exists.

    :param file: The file to create a directory structure for
    :return: None
    """
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
