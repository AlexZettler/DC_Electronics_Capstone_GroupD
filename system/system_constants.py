from data_handling.data_classes import Temperature

# Define min and max element temperatures
element_max_temp = Temperature(65.0)
element_min_temp = Temperature(-20.0)

# Define the system loop delay
system_update_interval = 0.2

# Define system pins
heating_pin = None
cooling_pin = None

# Use this for a relative path
base_log_directory = "./log/"
