# Generalized system configuration data
from system import system_constants

# Logging and handling sensitive stuff
from data_handling.custom_errors import OverTemperature, UnderTemperature
from data_handling import custom_logger

# Data types
from data_handling.data_classes import Temperature
from time import sleep


import datetime
import time

# System components
from system.sensors import TargetTemperatureSensor, ElementSensor, TemperatureSensor
from system.active_components import Element, RegisterFlowController

# Setup system logger
system_logger = custom_logger.create_system_logger()


class System(object):
    """
    This is the class for the main system

    """
    def __init__(self):
        self.element = Element("elem", peltier_heating=True, enabled=False)
        self.room_sensors = dict()
        self.room_dampers = dict()

        # define ids for rooms
        room_ids = range(1, 3)

        # Setup dampers and sensors for each room
        for _id in room_ids:
            self.room_sensors[_id] = TemperatureSensor(_id=_id)
            self.room_dampers[_id] = RegisterFlowController(id=_id, pin=None)


    def handle_cycle(self):
        pass

    def enter_main_loop(self)->None:
        """
        Method fo entering the main system control loop
        :return:
        """
        # Log system startup information
        system_logger.info("System is starting up!")

        while True:

            cycle_start_time = time.time()
            self.handle_cycle()
            cycle_end_time = time.time()

            delta_time = cycle_end_time - cycle_start_time

            # Todo: format time to be more readable
            system_logger.debug(f"Main loop completed in{delta_time}")

            sleep_time = system_constants.system_update_interval - delta_time

            if sleep_time>=0:
                time.sleep(sleep_time)
            else:
                system_logger.warning(
                    f"Main loop took longer than {system_constants.system_update_interval} to complete."
                    f"Consider changing the cycle time to a value greater than {delta_time}"
                    f"to ensure cycle time is consistent!"
                )


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
    element = Element("elem", peltier_heating=True, enabled=False)

    # Define room valves
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
