import logging
import os.path

from data_handling.data_classes import Temperature

#########################
# Temperature constants #
#########################

# Define min and max element temperatures
element_max_temp = Temperature(65.0)
element_min_temp = Temperature(-20.0)

##################
# Time constants #
##################

# Define the system loop delay
system_update_interval = 0.2

##################
# Pin constants #
##################

# Define system pins
heating_pin, cooling_pin = 23, 24

# Define room pins from ID: pin_name pair
room_servo_pins = {_id: pin_name for _id, pin_name in enumerate(iterable=(13, 19, 26))}

# todo: gather UUIDs for each sensor
room_temp_UUID_list = []
# Define room sensors from ID: UUID pair
room_temperature_UUIDS = {_id: pin_name for _id, pin_name in enumerate(iterable=room_temp_UUID_list)}

#####################
# Logging constants #
#####################

# Use this for a relative path
base_log_directory = "./log/"

# Define directories to place log files into
log_directories = {
    "measurements": os.path.join(base_log_directory, "measurements"),
    "outputs": os.path.join(base_log_directory, "outputs"),
    "system": base_log_directory
}

# Define a format to be used with reading and writing data to log files
csv_formatter = logging.Formatter(
    fmt="%(asctime)s, %(levelname)s, %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Define a format to be used with writing data to the python console
cons_formatter = logging.Formatter(
    fmt="%(asctime)s:%(levelname)s:%(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
