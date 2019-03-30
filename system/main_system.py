"""
The main system definition file
"""

# Generalized system configuration data
import datetime
import time
from threading import Lock, Thread
import queue

from time import sleep

import itertools

# General BT stuff
from bluetooth import *

# Logging and handling sensitive stuff
from data_handling import custom_logger
from data_handling.custom_errors import OverTemperature, UnderTemperature

# A bluetooth logging module used for sending new events over bluetooth
# from bluetooth_connection import bluetooth_logging_handler

# Data types
from data_handling.data_classes import Temperature
from system import system_constants
from system.active_components import Element, RegisterFlowController

# System components
from system.sensors import TargetTemperatureSensor, ElementSensor, TemperatureSensor, W1Bus, TemperatureNotFound

# Setup system logger
system_logger = custom_logger.create_system_logger()


# Add bluetooth handler to basic system logger
# system_logger.addHandler(bluetooth_logging_handler.BTHandler())


class SystemUpdate(object):
    """
    This object is responsible for representing an update to the system.
    This could be sent from the bluetooth device, or user input in a seperate command parsing process
    """

    def __init__(self, update_time: datetime.datetime, update_name: str, update_value: object):
        self.update_time = update_time
        self.update_name = update_name
        self.update_value = update_value


class BluetoothManager(object):
    def __init__(self):
        self.bt_lock = Lock()
        self.initialize_connection()
        self.setup_threads()

    def initialize_connection(self):
        # Configure bluetooth socket_server
        self.socket_server = BluetoothSocket(RFCOMM)
        self.socket_server.bind(("", PORT_ANY))
        self.socket_server.listen(1)

        # Get the port that the socket_server it bound to
        self.port = self.socket_server.getsockname()[1]

        self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    def setup_threads(self) -> None:
        """
        Setup threads for transmission and receiving
        :return: None
        """
        self.receiver_thread = Thread(target=self.receiver_loop, name=None, args=(), kwargs={}, daemon=None)
        self.transmitter_thread = Thread(target=self.transmitter_loop, name=None, args=(), kwargs={}, daemon=None)

        self.receiver_thread.start()
        self.transmitter_thread.start()

    def transmitter_loop(self):
        shared_queue = None
        while True:
            for d in shared_queue:
                self.send_string(d)

    def receiver_loop(self):
        shared_queue = None
        while True:
            for d in shared_queue:
                self.receive_data()

    def advertise_service(self):
        advertise_service(
            server_sock, "SampleServer",
            service_id=uuid,
            service_classes=[uuid, SERIAL_PORT_CLASS],
            profiles=[SERIAL_PORT_PROFILE],
            # protocols = [ OBEX_UUID ]
        )

    def stop_server(self):
        self.socket_server.close()
        print("Server stopped")

    def wait_for_client(self):

        print(f"Waiting for connection on RFCOMM channel {self.port}")

        self.client_sock, self.client_info = self.socket_server.accept()
        print(f"Accepted connection from {self.client_info}")

    def receive_data(self):

        try:
            while True:
                data = self.socket_server.recv(1024)
                if len(data) == 0:
                    break

                print(f"received [{data}]")

        except IOError:
            self.client_disconnected()

    def send_string(self, _string):
        print("Transmission begun.")
        # for p in break_string_into_segmented_byte_list(_string, None):
        self.client_sock.send(_string)

        print("Transmission complete.")

    def client_disconnected(self):
        self.client_sock = None
        self.client_info = None
        self.client_sock.close()

        print("Client disconnected")

    def advertise_service(self):
        advertise_service(
            server_sock, "SampleServer",
            service_id=uuid,
            service_classes=[uuid, SERIAL_PORT_CLASS],
            profiles=[SERIAL_PORT_PROFILE],
            # protocols = [ OBEX_UUID ]
        )


class InvalidCommand(Exception):
    pass


class UpdateHandler(object):
    def __init__(self):
        self.wait_for_input_command()

    def wait_for_input_command(self):

        try:
            while True:
                inp = input("Please enter a command: ")
                try:
                    cmd = self.input_parse(inp)
                    self.command_dispatch(cmd)
                except InvalidCommand:
                    pass
        except KeyboardInterrupt:
            pass

    def input_parse(self, inp):
        cmd_args = inp.split()

        # cmd_args[0]

    def command_dispatch(self):
        pass


def queue_drain(q):
    """
    Iterates through a queue until no items remain
    :param q: The Queue to retrieve items from
    :yield: Items from the queue
    """
    while True:
        try:
            yield q.get_nowait()
        except queue.Empty:
            break


class System(object):
    """
    This class represents the main system.
    It is used for setting up the system, running cycles, and monitoring performance.
    """

    def __init__(self):
        self.update_interval = system_constants.system_update_interval

        self.element = Element("element", peltier_heating=True)
        self.element.enabled = True
        self.element.apply_state()

        # Define sensor and damper management hash tables
        self.room_sensors = dict()
        self.room_dampers = dict()

        self.external_temperature_sensor = TemperatureSensor(
            "external", system_constants.external_sensor_UUID["external"])

        self.temperature_output_sensor = TemperatureSensor(
            "out", system_constants.temperature_output_sensor_UUID["out"])

        # define ids for rooms
        room_ids = range(3)

        connected_uuids = W1Bus()
        for _uuid in system_constants.sensor_UUIDS:
            if _uuid not in connected_uuids:
                system_logger.warning(f"The temperature sensor with ID: {_uuid} was unable to be located on the 1W-BUS")

        # Setup dampers and sensors for each room
        for _id in room_ids:
            # todo: Gather target temperature
            self.room_sensors[_id] = TargetTemperatureSensor(
                _id=_id,
                _uuid=system_constants.sensor_UUIDS[_id],
                target_temperature=Temperature(system_constants.room_temp_targets[_id]))

            system_logger.info(f"Room {_id} target temp is: {self.room_sensors[_id].target_temp}")

            self.room_dampers[_id] = RegisterFlowController(
                _id=_id,
                pin=system_constants.room_servo_pins[_id],
                min_duty=15.0,
                max_duty=25.0,
            )

        # Setup element sensors
        self.element_sensors = {
            "prim": ElementSensor(
                _id="prim",
                _uuid=system_constants.sensor_UUIDS["prim"],
                max_temp=system_constants.element_max_temp,
                min_temp=system_constants.element_min_temp
            ),
            "sec": ElementSensor(
                _id="sec",
                _uuid=system_constants.sensor_UUIDS["sec"],
                max_temp=system_constants.element_max_temp,
                min_temp=system_constants.element_min_temp
            )
        }

    def get_all_sensors_iterable(self):
        """
        Retrieves an iterable of all temperature sensors in the system
        """
        ret_iterable = itertools.chain(
            [self.external_temperature_sensor],

            self.room_sensors.values(),
            self.element_sensors.values()
        )
        return ret_iterable

    def get_temperature_readings(self):
        """
        Retrieves all temperature sensor readings

        :return:
        """

        # Generate a queue for putting temperature values from threads
        temp_reading_queue = queue.Queue()

        threads = []

        # Instantiate temperature reading threads
        # as the reading process can take up to a second per read
        for temp_sensor in self.get_all_sensors_iterable():
            temp_gather_thread = Thread(
                target=temp_sensor.get_temperature_c_into_queue,
                args=(temp_reading_queue,),
                kwargs={}
            )
            threads.append(temp_gather_thread)
            temp_gather_thread.start()

        # Wait for all reads to complete
        for t in threads:
            t.join()

        # Create a dictionary to store room temperature data
        room_readings = {}

        # Create a dictionary to store element temperature data
        element_sensor_readings = {}

        # Create a list of external temperature readings
        external_temperature_readings = []

        # Handle the queue temperature readings
        for sensor, reading in queue_drain(temp_reading_queue):
            if isinstance(sensor, ElementSensor):

                # Store temperature reading in the dictionary
                element_sensor_readings[sensor.get_id] = reading

                # Gather and check for temperatures over the element limits
                try:
                    sensor.check_temperature_limits(reading)

                # Disables the element in an over/under temperature condition
                except OverTemperature or UnderTemperature:
                    self.element.enabled = False

            elif isinstance(sensor, TargetTemperatureSensor):
                # This is a case of a room temperature

                room_readings[sensor.get_id] = reading

            elif isinstance(sensor, TemperatureSensor):
                # This will be the case for the previous 2 conditions as well,
                # This implies that the measurement was taken from the external sensor

                external_temperature_readings.append(reading)

            else:
                raise TemperatureNotFound

        # Return all readings that were gathered
        return external_temperature_readings, room_readings, element_sensor_readings

    def get_room_temperature_errors(self, readings: dict) -> dict:
        """

        :param readings:
        :return:
        """

        # Define the dict to return
        room_error_readings = {}

        # Calculate the temperature delta for each room
        for _id, reading in readings.items():
            # Calculates the temperature delta for the room and stores the delta temperature in a dictionary
            room_error_readings[_id] = self.room_sensors[_id].temperature_error(reading)

        return room_error_readings

    def handle_cycle(self) -> None:
        """
        Method for running a system cycle

        :return: None
        """

        # Retrieve temperature data
        external_temperature_readings, room_readings, element_sensor_readings = self.get_temperature_readings()

        # Create a dictionary to store all temperature errors
        room_error_readings = self.get_room_temperature_errors(room_readings)

        print(room_error_readings)

        # Iterate through each room
        for _id, servo in self.room_dampers.items():

            if self.element.enabled:

                # If system in heating mode and the room temperature is still below the target
                if self.element.heating and room_error_readings[_id].celsius <= 0.0:
                    servo.rotate_to_angle(90.0)

                # If system in cooling mode and the room temperature is still above the target
                elif self.element.cooling and room_error_readings[_id].celsius >= 0.0:
                    servo.rotate_to_angle(90.0)

                # The case if the temperature target has not been reached given the current system state
                else:
                    servo.rotate_to_angle(0.0)

            # Dampers should be closed when the system is off
            else:
                servo.rotate_to_angle(90.0)

        # Decide if the system should change temperature modes
        self.decide_target_direction(room_error_readings)

    def decide_target_direction(self, error_readings):
        """
        Decide on a target direction based on error readings
        Sets the system into the given target direction

        :param error_readings:
        :return:
        """
        # Define a error vector in out target temperature direction
        dir_error_total = 0.0

        # Now we need to decide if our current temperature target has been reached in the current temperature mode
        if self.element.heating:

            # Only cumulative reading in our target direction
            for e in error_readings:
                if e > 0.0:
                    dir_error_total += e

        else:
            for e in error_readings:
                if e < 0.0:
                    dir_error_total += e

        # Catch temperature in direction satisfied
        if dir_error_total == 0.0:
            # Switch heating/cooling direction
            self.element.heating = self.element.cooling

            # self.element.enabled = True

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

    def get_delay_time(self, cycle_time: float) -> float:
        """
        Gets the desired delay time from a cycle duration.

        :param cycle_time: The desired cycle time in seconds
        :return:
        """
        sleep_time = self.update_interval - cycle_time

        # Handle case where sleep time is less than 0.
        # This is the case when the cycle time is greater than the update interval
        if sleep_time < 0:
            # Log a warning with time information about the cycle
            system_logger.warning(
                f"Main loop took longer than {self.update_interval} to complete."
                f"Consider changing the cycle time to a value greater than {cycle_time}"
                f"to ensure cycle time is consistent!"
            )
            sleep_time = 0.0

        return sleep_time


if __name__ == "__main__":
    # run_system()
    sys = System()
