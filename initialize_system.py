import multiprocessing as mp

from data_classes import Temperature
from system_components import TemperatureSensor, TargetTemperatureSensor, ElementMonitor



def run_temperature_monitoring():
    element_max_temp = Temperature(65.0)
    element_min_temp = Temperature(-20.0)

    print(f"{'*'*26}\n* System is starting up! *\n{'*'*26}")

    room_temperature_sensors = [TargetTemperatureSensor(id, Temperature(20)) for id in range(3)]

    print(room_temperature_sensors)

    primary_element = ElementMonitor("prim", element_max_temp, element_min_temp)
    secondary_element = ElementMonitor("sec", element_max_temp, element_min_temp)


def run_system():
    #q = mp.Queue()
    run_temperature_monitoring()

if __name__ == "__main__":
    run_system()