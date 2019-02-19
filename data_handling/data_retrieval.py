from system.system_constants import base_log_directory

from data_handling.custom_logger import csv_formatter, log_directories

from typing import Generator
import random
import os
import datetime
import csv


def get_device_types():
    return log_directories.keys()


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


def iget_files_in_directory(dir, ext: str):
    """
    Generator function to retrieve all files in a given folder

    :param dir: The directory to retrieve the files from
    :param ext: The File extension to filter out of the directory
    :yield: File Paths
    """
    for item in os.listdir(dir):
        if os.path.isfile(dir) and (item.split(".")[-1] == ext):
            yield item
    raise StopIteration


def iget_file_readings(csv_file_path):
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


def time_filter(start_time: datetime.datetime, end_time: datetime.datetime):
    """
    Generator function to iterate through a Generator statement
    and return measurements that fall within the specified time range
    """

    # Undefined start
    if start_time is None:
        pass

    if end_time is None:
        end_time = datetime.datetime.now()

    # todo: write this as a wrapper function
    def decorate(func):
        def call(*args, **kwargs):
            for data in func(*args, **kwargs):
                time_valid = True
                # todo: figure out where the timestamp is located in the data

                data_timestamp = datetime.datetime.strptime(data[0],csv_formatter.datefmt)

                # Filter out results that are outside of the datetime range
                if start_time > data_timestamp:
                    time_valid = False
                if data_timestamp < data_timestamp:
                    time_valid = False

                # Only yield results within the range
                if time_valid:
                    yield data

            # Stop the yield loop
            raise StopIteration

        return call
    return decorate


def priority_filter(funct):
    # todo: implement this as a generator function wrapper function
    def wrapper():
        pass


def iget_time_filtered_data(csv_file_path, start_time, end_time):
    """
    A generator function to return data-points within a certain time-range

    :param csv_file_path:   The file-path of the csv file to retrieve values from
    :param start_time:      The time to start yielding data
    :param end_time:        The time to stop yielding data
    :yield:             Data within the time-range
    """
    @time_filter(start_time, end_time)
    def get_data():
        for data in iget_file_readings(csv_file_path):
            yield data
        raise StopIteration
    get_data()


def iget_deltatime_filtered_data(csv_file_path, time_delta: datetime.timedelta):
    """
    A generator function to return data-points that were logged within the last timedelta

    :param csv_file_path:   The file-path of the csv file to retrieve values from
    :param time_delta:      The time delta from the current time to start filtering data from
    :yield:                 Data within the time-range
    """

    # Calculate the start time from the end time and time delta
    end_time = datetime.datetime.now()
    start_time = end_time - time_delta

    @time_filter(start_time, end_time)
    def get_data():
        for data in iget_file_readings(csv_file_path):
            yield data
        raise StopIteration
    return get_data()



def get_rand_data():
    return [[random.random() for i in range(25)]for i in range(5)]

if __name__ == "__main__":
    # print(self.get_devices_from_log_directory("../log"))

    # Create the path to retrieve measurements from
    file_name = os.path.join(log_directories["measurements"], f"dummy.csv")
    td = datetime.timedelta(minutes=1)

    # Retrieve data from generator wrapper
    data = iget_deltatime_filtered_data(csv_file_path=file_name, time_delta=td)
    f_data = '\n'.join([f"{time}: {value}" for time, log_level, value in data])
    print(f"Data is as follows:\n{f_data}")
