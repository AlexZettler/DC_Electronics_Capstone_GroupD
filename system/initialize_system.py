# Generalized system configuration data
from system import system_constants

# Logging and handling sensitive stuff
from data_handling.custom_errors import OverTemperature, UnderTemperature
from data_handling import custom_logger

# Data types
from data_handling.data_classes import Temperature
from time import sleep
import datetime

# System components
from system.sensors import TargetTemperatureSensor, ElementSensor, TemperatureSensor
from system.active_components import Element, RegisterFlowController

# Setup system logger
system_logger = custom_logger.create_system_logger()


def run_system():
    # Log system startup information
    system_logger.info("System is starting up!")

    # Setup external temperature sensor
    external_temp_sensor = TemperatureSensor("external")

    # Setup room sensors
    room_temperature_sensors = [TargetTemperatureSensor(id, Temperature(20)) for id in range(3)]

    # Setup element sensors
    primary_element_monitor = ElementSensor("prim", system_constants.element_max_temp,
                                            system_constants.element_min_temp)
    secondary_element_monitor = ElementSensor("sec", system_constants.element_max_temp,
                                              system_constants.element_min_temp)

    # Set up our active components
    element = Element(peltier_heating=True, enabled=False)
    register_valves = [RegisterFlowController(id, "Dummy pin") for id in range(3)]

    # Enable the main temperature control loop of the element
    element.enabled = True

    # Log our current time to get system loop operating time
    previous_time = datetime.datetime.now()

    # Enter the infinite loop!
    while True:

        # Gather and check for temperatures over the element limits
        for es in (primary_element_monitor, secondary_element_monitor):
            element_temp = es.get_temperature()
            try:
                es.check_temperature_limits(element_temp)
            except OverTemperature or UnderTemperature:
                # Disables the element in an over/under temperature condition
                element.enabled = False

        # Iterate through each room and get the temperatures
        room_readings = []
        for ts in room_temperature_sensors:
            # Gets the current room temperature
            current_room_temp = ts.get_temperature()

            # Calculates the temperature delta for the room
            room_readings.append(ts.temperature_error(current_room_temp))

        # Calculate the system overall target vector based on a pid controller
        element.generate_new_target_vector(external_temp_sensor.get_temperature(), room_readings)

        # Wait a period of time defined
        sleep(system_constants.system_update_interval)

        # Log a complete system loop and the time it took to complete
        system_logger.debug(f"Main loop completed in {(datetime.datetime.now() - previous_time).total_seconds()}s")
        previous_time = datetime.datetime.now()


if __name__ == "__main__":
    run_system()
