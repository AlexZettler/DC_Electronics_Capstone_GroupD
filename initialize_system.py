import system_constants
import logging
from custom_errors import OverTemperature, UnderTemperature
import custom_logger
from time import sleep
import datetime

from data_classes import Temperature
from sensors import TargetTemperatureSensor, ElementMonitor, TemperatureSensor
from active_components import Element, RegisterFlowController



system_logger = custom_logger.create_system_logger()

def run_system():

    print(f"{'*'*26}\n* System is starting up! *\n{'*'*26}")

    extern_temp_sensor = TemperatureSensor("exter")

    # Setup room sensors
    room_temperature_sensors = [TargetTemperatureSensor(id, Temperature(20)) for id in range(3)]

    # Setup element sensors
    primary_element_monitor = ElementMonitor("prim", system_constants.element_max_temp, system_constants.element_min_temp)
    secondary_element_monitor = ElementMonitor("sec", system_constants.element_max_temp, system_constants.element_min_temp)

    # Set up our active components
    element = Element(peltier_heating=True, enabled=False)
    register_valves = [RegisterFlowController(id, "Dummy pin") for id in range(3)]

    # Enable the main temperature control loop of the element
    element.enabled = True

    # Log our current time to get system loop operating time
    previous_time = datetime.datetime.now()

    # Enter the infinite loop!
    while True:

        for es in (primary_element_monitor, secondary_element_monitor):
            element_temp = es.get_temperature()
            try:
                es.check_temperature_limits(element_temp)
            except OverTemperature or UnderTemperature:
                element.enabled = False

        # Iterate through each room and get the temperatures
        room_readings = []
        for ts in room_temperature_sensors:
            # Gets the current room temperature
            current_room_temp = ts.get_temperature()

            # Calculates the temperature delta for the room
            room_readings.append(ts.calculate_temperature_delta(current_room_temp))

        # Calculate the system overall target vector based on a pid controller
        element.generate_new_target_vector(extern_temp_sensor.get_temperature(), room_readings)

        # Wait a period of time defined
        sleep(system_constants.system_update_interval)


        system_logger.debug(f"Main loop completed in {(datetime.datetime.now() - previous_time).total_seconds()}s")
        previous_time = datetime.datetime.now()

if __name__ == "__main__":
    run_system()