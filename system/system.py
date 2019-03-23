"""
The main system definition file
"""

# Generalized system configuration data
import datetime
import time
from threading import Lock, Thread
from time import sleep

# General BT stuff
from bluetooth import *

# Logging and handling sensitive stuff
from data_handling import custom_logger
from data_handling.custom_errors import OverTemperature, UnderTemperature

# A bluetooth logging module used for sending new events over bluetooth
#from bluetooth_connection import bluetooth_logging_handler

# Data types
from data_handling.data_classes import Temperature
from system import system_constants
from system.active_components import Element, RegisterFlowController

# System components
from system.sensors import TargetTemperatureSensor, ElementSensor, TemperatureSensor, W1Bus

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


class System(object):
    """
    This class represents the main system.
    It is used for setting up the system, running cycles, and monitoring performance.
    """

    def __init__(self):
        self.update_interval = system_constants.system_update_interval

        self.element = Element("element", peltier_heating=True)

        # Define sensor and damper management hash tables
        self.room_sensors = dict()
        self.room_dampers = dict()

        #todo: ADD UUID HERE
        self.external_temperature_sensor = TemperatureSensor("external", None)

        # define ids for rooms
        room_ids = range(1, 3)

        connected_uuids = W1Bus()
        for _uuid in system_constants.room_temp_UUID_list:
            if _uuid not in connected_uuids:
                print(f"The temperature sensor with ID: {_uuid} was unable to be located on the 1W-BUS")

        # Setup dampers and sensors for each room
        for _id in room_ids:
            # todo: Gather target temperature
            self.room_sensors[_id] = TargetTemperatureSensor(
                _id=_id,
                _uuid=system_constants.room_temperature_UUIDS[_id],
                target_temperature=Temperature(20.0))

            self.room_dampers[_id] = RegisterFlowController(
                _id=_id,
                pin=system_constants.room_temperature_UUIDS[_id])

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

        :return: None
        """

        # Get external temperature
        external_temp = self.external_temperature_sensor.get_temperature_c()

        # Gather and check for temperatures over the element limits
        for es in self.element_sensors:
            element_temp = es.get_temperature_c()
            try:
                es.check_temperature_limits(element_temp)

            # Disables the element in an over/under temperature condition
            except OverTemperature or UnderTemperature:
                self.element.enabled = False

        # Iterate through each room and get the temperatures
        room_readings = {}
        for _id, sensor in self.room_sensors.items():
            # Gets the current room temperature
            current_room_temp = sensor.get_temperature_c()

            # Calculates the temperature delta for the room
            delta_temp = sensor.temperature_error(current_room_temp)

            # Stores the delta temperature in a dictionary with shared sensor keys
            room_readings[_id] = delta_temp

        # Calculate the system overall target vector based on a pid controller
        # todo: implement this!
        self.element.generate_target_vector(external_temp, room_readings)

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


def run_system(incoming_update_queue=None):
    """
    This function is being replaced by the System class
    """

    # Log system startup information
    system_logger.info("System is starting up!")

    # Setup external temperature sensor
    external_temp_sensor = TemperatureSensor("external")

    # Setup room sensors
    room_temperature_sensors = [TargetTemperatureSensor(_id, Temperature(20.0)) for _id in range(3)]

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

        if incoming_update_queue is not None:
            pass

        # Gather and check for temperatures over the element limits
        for es in (primary_element_monitor, secondary_element_monitor):
            element_temp = es.get_temperature_c()
            try:
                es.check_temperature_limits(element_temp)
            except OverTemperature or UnderTemperature:
                # Disables the element in an over/under temperature condition
                element.enabled = False

        # Iterate through each room and get the temperatures
        room_readings = []
        for ts in room_temperature_sensors:
            # Gets the current room temperature
            current_room_temp = ts.get_temperature_c()

            # Calculates the temperature delta for the room
            room_readings.append(ts.temperature_error(current_room_temp))

        # Calculate the system overall target vector based on a pid controller
        element.generate_target_vector(external_temp_sensor.get_temperature_c(), room_readings)

        # Wait a period of time defined
        sleep(system_constants.system_update_interval)

        # Log a complete system loop and the time it took to complete
        system_logger.debug(f"Main loop completed in {(datetime.datetime.now() - previous_time).total_seconds()}s")
        previous_time = datetime.datetime.now()


if __name__ == "__main__":
    # run_system()
    sys = System()
