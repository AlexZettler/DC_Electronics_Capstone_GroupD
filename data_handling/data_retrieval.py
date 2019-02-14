from data_handling import custom_logger
from data_handling.custom_logger import base_directory, csv_formatter

import random
import os
import datetime
import csv


def get_device_types():
    return custom_logger.log_directories.keys()

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

def iget_file_reading(csv_file_path):
    with open(csv_file_path, mode="r") as f:
        csvreader = csv.reader(f, quotechar='|')
        for row in csvreader:
            #print(row)
            time, level, reading = row
            yield (time, level, reading)
    raise StopIteration

def iget_time_filtered_readings(csv_file_path, time_range: tuple):
    start_time, end_time = time_range
    if end_time < start_time:
        start_time, end_time = end_time, start_time
    print(f"{start_time} to {end_time}")

    for row_data in iget_file_reading(csv_file_path):
        # print(row_data)
        time, level, reading = row_data
        time = datetime.datetime.strptime(time, csv_formatter.datefmt)

        if end_time > time > start_time:
            yield (time, reading)
    raise StopIteration

def iget_data_from_time_delta(file_name, time_delta):
    # Test temperature reading
    current_time = datetime.datetime.now()
    previous_time = current_time - time_delta

    for time,value in iget_time_filtered_readings(file_name, (current_time, previous_time)):
        yield (time, value)
    raise StopIteration

def get_rand_data():
    return [[random.random() for i in range(25)]for i in range(5)]

#print(self.get_devices_from_log_directory("../log"))