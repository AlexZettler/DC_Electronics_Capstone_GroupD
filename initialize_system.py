from data_classes import Temperature
from system_components import TemperatureMonitor, RoomMonitorController


# Setup Logger

# Setup Configuration monitor

# Setup room monitoring


room_temperature_sensors = [TemperatureMonitor(Temperature(20)) for i in range(5)]
print(room_temperature_sensors)


rmc = RoomMonitorController(room_temperature_sensors)
print(rmc.__dict__)

#total_temperature_delta = sum(temp.target_temp for temp in room_temperature_sensors)





# Setup Room Flow Controls

# Setup Heater