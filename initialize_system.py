#import multiprocessing as mp
import system_constants
from time import sleep

from data_classes import Temperature
from sensors import TargetTemperatureSensor, ElementMonitor, Element


def run_temperature_monitoring():

    print(f"{'*'*26}\n* System is starting up! *\n{'*'*26}")

    room_temperature_sensors = [TargetTemperatureSensor(id, Temperature(20)) for id in range(3)]

    element = Element(peltier_heating=True, enabled=False)

    primary_element_monitor = ElementMonitor("prim", element, system_constants.element_max_temp, system_constants.element_min_temp)
    secondary_element_monitor = ElementMonitor("sec", element, system_constants.element_max_temp, system_constants.element_min_temp)

    #Enter the infinite loop!
    while True:

        for es in (primary_element_monitor, secondary_element_monitor):
            # Every sensor is linked to the element
            # and disables the element in an extreme temperature situation
            es.get_temperature()

        #Iterate through each room and get the temperatures
        room_readings = []
        for ts in room_temperature_sensors:
            # Gets the current room temperature
            current_room_temp = ts.get_temperature()

            # Calculates the temperature delta for the room
            room_readings.append(ts.calculate_temperature_delta(current_room_temp))

        # Calculate the system overall target vector based on a pid controller
        element.generate_new_target_vector(room_readings)

        # Wait a period of time defined
        sleep(system_constants.system_update_interval)


def run_system():
    run_temperature_monitoring()

if __name__ == "__main__":
    run_system()