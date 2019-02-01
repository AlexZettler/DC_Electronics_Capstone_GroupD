from data_classes import Temperature
from system_components import TemperatureMonitor


# Setup Logger

# Setup Configuration monitor

# Setup room monitoring


room_temperature_sensors = [TemperatureMonitor(Temperature(20)) for i in range(5)]



total_temperature_delta = sum(temp for temp in room_temperature_sensors)





# Setup Room Flow Controls

# Setup Heater