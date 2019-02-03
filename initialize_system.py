import multiprocessing as mp
import system_constants
from time import sleep

from data_classes import Temperature
from sensors import TemperatureSensor, TargetTemperatureSensor, ElementMonitor, Element


def run_temperature_monitoring():
    element_max_temp = Temperature(65.0)
    element_min_temp = Temperature(-20.0)

    print(f"{'*'*26}\n* System is starting up! *\n{'*'*26}")

    room_temperature_sensors = [TargetTemperatureSensor(id, Temperature(20)) for id in range(3)]

    print(room_temperature_sensors)

    element = Element(peltier_heating=True, enabled=False)

    primary_element_monitor = ElementMonitor("prim", element, element_max_temp, element_min_temp)
    secondary_element_monitor = ElementMonitor("sec", element, element_max_temp, element_min_temp)


    while True:

        temperature_limit_exceeded = False

        for es in (primary_element_monitor, secondary_element_monitor):
            es.get_temperature()

            if es.temperature_lock:
                temperature_limit_exceeded = True

        if temperature_limit_exceeded:
           element.enabled = False

        for ts in room_temperature_sensors:
            ts.get_temperature()

        sleep(0.2)

def run_system():
    #q = mp.Queue()
    run_temperature_monitoring()

if __name__ == "__main__":
    run_system()