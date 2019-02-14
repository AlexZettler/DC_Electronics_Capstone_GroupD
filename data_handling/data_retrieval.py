from data_handling import custom_logger
from data_handling.custom_logger import base_log_directory, csv_formatter

from typing import Generator
import random
import os
import datetime
import csv


def get_device_types():
    return custom_logger.log_directories.keys()


def iget_log_dirs():
    """
    Generator function to retrieve all folders in the log directory path.
    Each folder represents a group of logs corresponding to the directory name

    :yield: Directory
    """
    for item in os.listdir(base_log_directory):
        if os.path.isdir(base_log_directory):
            yield item
    raise StopIteration


def iget_csv_files_in_directory(dir):
    """
    Generator function to retrieve all csv files in a given folder

    :param dir: The directory to retrieve the files from
    :yield: File Path
    """
    for item in os.listdir(dir):
        if os.path.isfile(dir) and (item.split(".")[-1] == "csv"):
            yield item
    raise StopIteration


def iget_file_reading(csv_file_path):
    """
    Generator function to get ALL data reading in a csv file

    :param csv_file_path: The location of the csv file
    :yield: Tuple of reading attributes
    """
    with open(csv_file_path, mode="r") as f:
        csv_reader = csv.reader(f, quotechar='|')
        for row in csv_reader:
            #print(row)
            time, level, reading = row
            yield (time, level, reading)
    raise StopIteration


def iget_time_filtered_readings(csv_file_path, time_range: tuple):
    # todo: break this down into a time filter function
    start_time, end_time = time_range
    if end_time < start_time:
        start_time, end_time = end_time, start_time
    print(f"{start_time} to {end_time}")

    for row_data in iget_file_reading(csv_file_path):
        # print(row_data)
        time, level, reading = row_data
        time = datetime.datetime.strptime(time, csv_formatter.datefmt)

        # Filter time reading between two times
        if end_time > time > start_time:
            yield (time, reading)
    raise StopIteration


def time_filter(data: Generator, time_range: tuple = (None, None)):
    """
    Generator function to iterate through a Generator statement
    and return measurements that fall within the specified time range

    :param data: A generator to iterate through
    :param time_range:
    :return:
    """
    start_time, end_time = time_range

    # Undefined start
    if start_time is None:
        pass

    if end_time is None:
        end_time = datetime.datetime.now()

    if end_time < start_time:
        start_time, end_time = end_time, start_time


    #print(f"{start_time} to {end_time}")


def iget_data_from_time_delta(csv_file_path, time_delta: datetime.timedelta):
    """
    Generator function to get a series of measurements
    to now from a previous time defined by a time delta.

    :param csv_file_path: The location of the csv file
    :param time_delta: The time in the past to retrieve the time from
    :return: 
    """
    # Test temperature reading
    current_time = datetime.datetime.now()
    previous_time = current_time - time_delta

    #
    for time, value in iget_time_filtered_readings(csv_file_path, (current_time, previous_time)):
        yield (time, value)
    raise StopIteration

def get_rand_data():
    return [[random.random() for i in range(25)]for i in range(5)]

#print(self.get_devices_from_log_directory("../log"))