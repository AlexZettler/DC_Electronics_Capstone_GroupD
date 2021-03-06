import logging
import os.path

from data_handling.data_classes import Temperature

#########################
# Temperature constants #
#########################

# Define min and max element temperatures
element_max_temp = Temperature(65.0)
element_min_temp = Temperature(-20.0)

# Define room temperature targets
room_temp_targets = [20, 24, 26]

##################
# Time constants #
##################

# Define the system loop delay
system_update_interval = 5.0

##################
# Pin constants #
##################

# Define system pins
heating_pin, cooling_pin = 23, 24

# Define room pins from ID: pin_name pair
room_servo_pins = {
    _id: pin_name for _id, pin_name in enumerate(iterable=(13, 19, 26))
}

# Define the shared PWM signal pin
shared_pwm_signal_pin = 12

# Define the pin to control fans
fan_enable_pin = 5

# Define room sensors from ID: UUID pair
room_temp_UUID_list = ["00000b0bd120", "00000b0be1c7", "00000b0bf3f0"]
room_temperature_UUIDS = {_id: pin_name for _id, pin_name in enumerate(iterable=room_temp_UUID_list)}

element_sensor_UUIDs = {
    "prim": "00000b0bd9e2",
    "sec": "00000b0bd7af"
}

# Define the external temperature around the system
external_sensor_UUID = {"external": "00000b0bdbe0"}

# Define the temperature output of the system
temperature_output_sensor_UUID = {"out": None}

# Create a complete dict of k:UUID sensor pairs
sensor_UUIDS = {
    **room_temperature_UUIDS,
    **element_sensor_UUIDs,
    **external_sensor_UUID,
    **temperature_output_sensor_UUID
}

######################
# Calibration values #
######################

servo_duty_calibrations = {
    0: (2.611111111111, 7.324691358024467),
    1: (3.1041014987555555, 7.7345679),
    2: (2.713580236, 7.2973662530666665),

}

#####################
# Logging constants #
#####################

# Use this for a relative path
base_log_directory = "/home/pi/ownCloud/Documents/Group4/system/log/"

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
