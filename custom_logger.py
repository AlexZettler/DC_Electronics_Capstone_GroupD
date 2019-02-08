import logging
import os
import os.path as path
from time import sleep
import datetime
import csv

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


def iget_log_dirs():
    for item in os.listdir(base_directory):
        if os.path.isdir(base_directory):
            yield item
    raise StopIteration


def iget_device_files_from_log_directory(dir):
    for item in os.listdir(dir):
        if os.path.isfile(dir) and (item.split(".")[-1] == "csv"):
            yield item
    raise StopIteration


def get_file_reading(csv_file_path):
    with open(csv_file_path, mode="r") as f:
        csvreader = csv.reader(f, quotechar='|')
        for row in csvreader:
            #print(row)
            time, level, reading = row
            yield (time, level, reading)
    raise StopIteration


def get_time_filtered_readings(csv_file_path, time_range: tuple):
    start_time, end_time = time_range
    if end_time < start_time:
        start_time, end_time = end_time, start_time
    print(f"{start_time} to {end_time}")

    for row_data in get_file_reading(csv_file_path):
        #print(row_data)
        time, level, reading = row_data
        time = datetime.datetime.strptime(time, csv_formatter.datefmt)

        if end_time > time > start_time:
            yield (time, reading)
    raise StopIteration


def get_data_from_time_delta(file_name, time_delta):
    # Test temperature reading
    current_time = datetime.datetime.now()

    previous_time = current_time - time_delta

    print(f"Printing data logged in the last minute:")
    for time,value in get_time_filtered_readings(file_name,(current_time, previous_time)):
        yield (time, value)



if __name__ == "__main__":
    system_logger = create_system_logger()
    system_logger.warning("the custom logger was run as a main script")

    dummy_sensor_logger = create_measurement_logger("dummy")
    file_name = os.path.join(log_directories["measurements"], f"dummy.csv")

    for i in range(5):
        dummy_sensor_logger.info(i)

    # todo: you finished here, need to format tuples to print
    data = get_data_from_time_delta(file_name=file_name, time_delta=datetime.timedelta(minutes=1, seconds=0))
    f_data = '\n'.join([*data])
    print(f_data)



#create_path_for_file("./lol/lol.txt")