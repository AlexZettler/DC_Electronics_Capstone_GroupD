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
    This class represents the main system.
    It is used for setting up the system, running cycles, and monitoring performance.
    """

    def __init__(self):
        self.update_interval = system_constants.system_update_interval

        self.element = Element("element", peltier_heating=True, enabled=False)

        # Define sensor and damper management hash tables
        self.room_sensors = dict()
        self.room_dampers = dict()

        # define ids for rooms
        room_ids = range(1, 3)

        # Setup dampers and sensors for each room
        for _id in room_ids:
            self.room_sensors[_id] = TemperatureSensor(_id=_id)
            self.room_dampers[_id] = RegisterFlowController(id=_id, pin=None)

        # Setup element sensors
        self.element_sensors = {
            name: ElementSensor(
                _id=name,
                max_temp=system_constants.element_max_temp,
                min_temp=system_constants.element_min_temp
            )
            for name in ("prim", "sec")
        }

    def handle_cycle(self) -> None:
        """
        Method for running a system cycle

        :return:
        """

        pass

    def enter_main_loop(self) -> None:
        """
        Method for entering the main system control loop
        :return:
        """
        # Log system startup information
        system_logger.info("System is starting up!")

        while True:
            # Get the cycle start time
            cycle_start_time = time.time()

            # Run the cycle
            self.handle_cycle()

            # Get the cycle end time
            cycle_end_time = time.time()

            # Calculate the cycle run time
            delta_time = cycle_end_time - cycle_start_time

            # Todo: format seconds decimal places
            system_logger.debug(f"Main loop completed in {delta_time}")

            # Get desired sleep time
            desired_delay_time = self.get_delay_time(delta_time)
            time.sleep(desired_delay_time)

    def get_delay_time(self, cycle_time):
        sleep_time = self.update_interval - cycle_time

        # Handle case where sleep time is less than 0.
        # This is the case when the cycle time is greater than the update interval
        if sleep_time < 0:
            # Log a warning with time information about the cycle
            system_logger.warning(
                f"Main loop took longer than {system_constants.system_update_interval} to complete."
                f"Consider changing the cycle time to a value greater than {cycle_time}"
                f"to ensure cycle time is consistent!"
            )
            sleep_time = 0.0

        return sleep_time


def run_system():
    """
    This function is being replaced by the System class
    """

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
