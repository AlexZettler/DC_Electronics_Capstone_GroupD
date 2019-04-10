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

from multiprocessing import Manager

# A bluetooth logging module used for sending new events over bluetooth
# from bluetooth_connection import bluetooth_logging_handler

# Data types
from data_handling.data_classes import Temperature
from system import system_constants
from system.active_components import Element, RegisterFlowController, DeviceEnabler

# System components
from system.sensors import TargetTemperatureSensor, ElementSensor, TemperatureSensor, W1Bus, TemperatureNotFound

from event_system.event_handler import EventHandler
from event_system.events import Event
from system.system_events import *

# Setup system logger
system_logger = custom_logger.create_system_logger()


# Add bluetooth handler to basic system logger
# system_logger.addHandler(bluetooth_logging_handler.BTHandler())

class BT_Server(object):
    """
    A Bluetooth server is a device which is responsible for managing the connection to client devices
    """

    def __init__(self):
        # Configure bluetooth socket_server
        self.server_socket = BluetoothSocket(RFCOMM)

        self.client_socket = None
        self.client_info = None

        self.event_thread = None

        self.server_socket.bind(("", PORT_ANY))
        self.server_socket.listen(1)

        # Get the port that the socket_server it bound to
        self.port = self.server_socket.getsockname()[1]

        self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        # self.advertise_BT_service()

    def wait_for_client(self):

        system_logger.info(f"Waiting for connection on RFCOMM channel {self.port}")
        self.client_socket, self.client_info = self.server_socket.accept()
        system_logger.info(f"Accepted connection from {self.client_info}")

    def advertise_BT_service(self):
        advertise_service(
            self.server_socket, "SampleServer",
            service_id=self.uuid,
            service_classes=[self.uuid, SERIAL_PORT_CLASS],
            profiles=[SERIAL_PORT_PROFILE],
            # protocols = [ OBEX_UUID ]
        )

    def stop_server(self):
        # Close both client and server sockets
        self.server_socket.close()
        self.client_socket.close()
        self.server_socket = None
        self.client_socket = None

        system_logger.info("BT Server stopped")

    def receive_data_to_queue_loop(self, _data_queue: queue.Queue):

        try:
            while True:
                data = self.server_socket.recv(1024)
                if len(data) == 0:
                    break
                _data_queue.put(data)
                system_logger.debug(f"received {data}")

        except IOError as e:
            self.client_disconnected()
            raise e

    def begin_data_receive_loop(self, _data_queue: queue.Queue):
        self.event_thread = Thread(
            target=self.receive_data_to_queue_loop,
            args=(_data_queue,),
            kwargs={}
        )
        self.event_thread.start()

    def send_string(self, _string):
        print("Transmission begun.")
        # for p in break_string_into_segmented_byte_list(_string, None):
        self.client_socket.send(_string)

        print("Transmission complete.")

    def client_disconnected(self):
        self.client_socket = None
        self.client_info = None
        self.client_socket.close()

        print("Client disconnected")


class InvalidCommand(Exception):
    pass


class StringCommandHandler(object):

    def __init__(self, handler: EventHandler, system):
        self.handler = handler
        self.system = system
        # self.get_input_loop()

    def start(self):
        t = Thread(target=self.get_input_loop)
        t.start()

    def get_input(self) -> str:
        raise NotImplementedError

    def get_input_loop(self):
        while True:
            inp = self.get_input()
            self.handle_input(inp)

    @staticmethod
    def input_parse(inp):
        cmd_args = inp.split()
        command = cmd_args[0]
        args = cmd_args[1:]
        return command, args

    def handle_input(self, inp):
        command, args = self.input_parse(inp)
        _event = None

        try:
            if command == "system":
                if args[0] == "start":
                    _event = SystemStartEvent(self.system.element)

                elif args[0] == "stop":
                    _event = SystemStopEvent(self.system.element)

                elif args[0] == "operation":
                    if args[1] == "mode":
                        if args[2] == "test":
                            _event = SystemOperationModeTestEvent(self.system)
                        elif args[2] == "auto":
                            _event = SystemOperationModeAutoEvent(self.system)
                        elif args[2] == "extreme":
                            _event = SystemOperationModeExtremeEvent(self.system)
                        else:
                            raise InvalidCommand
                        raise InvalidCommand
                    else:
                        raise InvalidCommand
                else:
                    raise InvalidCommand

            elif command == "element":
                if args[0] == "set":
                    if args[1] == "heat":
                        _event = ElementHeatEvent(self.system.element)
                    elif args[1] == "cool":
                        _event = ElementCoolEvent(self.system.element)
                    elif args[1] == "heat+cool":
                        _event = ElementHeatAndCoolEvent(self.system.element)
                    else:
                        raise InvalidCommand

                elif args[0] == "get":
                    if args[1] == "status":
                        _event = ElementGetStatus(
                            self.system.element,
                            self.system.system.bt_connection)
                    else:
                        raise InvalidCommand
                else:
                    raise InvalidCommand

            elif command == "room":
                target_room = int(args[0])

                if args[1] == "set":

                    if args[2] == "angle":
                        angle = float(args[3])
                        _event = RegisterRotateEvent(self.system.room_dampers[target_room], angle)

                    elif args[2] == "pwm":
                        pwm = float(args[3])
                        _event = RegisterPWMEvent(self.system.room_dampers[target_room], pwm)

                    elif args[2] == "open":
                        _event = RegisterOpenEvent(self.system.room_dampers[target_room])

                    elif args[2] == "close":
                        _event = RegisterCloseEvent(self.system.room_dampers[target_room])

                    elif args[2] == "temp":
                        new_temp = Temperature(float(args[2]))
                        _event = TemperatureTargetUpdatedEvent(self.system.room_sensors[target_room], new_temp)

                    else:
                        raise InvalidCommand

                elif args[1] == "get":
                    if args[2] == "status":
                        # todo: Figure out how to get this to send the value to the requested target
                        temp = self.system.room_sensors[target_room]

                    else:
                        raise InvalidCommand
                else:
                    raise InvalidCommand

            elif command == "fan":
                if args[0] == "set":
                    if args[1] == "on":
                        pass
                    elif args[1] == "off":
                        pass
                    else:
                        raise InvalidCommand

                elif args[0] == "get":
                    if args[1] == "status":
                        pass
                else:
                    raise InvalidCommand
            else:
                raise InvalidCommand
            # Completed argument handling

            # Handle the actual event if no errors were raised
            if isinstance(_event, Event):
                self.command_dispatch(_event)

            else:
                system_logger.warning(f"Unassigned command with arguments: {inp}")

        # Except an error with invalid arguments
        except (InvalidCommand, KeyError):
            system_logger.warning(f"Invalid command: {inp}")

    def command_dispatch(self, _event):
        self.handler.add_event(_event)


class BluetoothCommandListener(StringCommandHandler):

    def __init__(self, handler: EventHandler, system):
        # self.wait_for_connection()
        self.bt_connection = BT_Server()
        self.bt_connection.advertise_BT_service()

        super().__init__(handler, system)

    def start(self):
        t = Thread(target=self.connect_accept_data_loop)
        t.start()

    def connect_accept_data_loop(self):
        while True:
            try:
                self.bt_connection.wait_for_client()
                self.bt_connection.begin_data_receive_loop(self.handler.event_queue)
            except IOError:
                pass


class CommandlineCommandHandler(StringCommandHandler):

    # todo: Add a new Popen process to get input from
    def __init__(self, handler: EventHandler, system):
        super().__init__(handler, system)
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

    def __init__(self, default_enabled: bool):
        # Retrieve target update time from system constants
        self.update_interval = system_constants.system_update_interval

        # Define the element and enable it
        self.element = Element("element", peltier_heating=True)

        self.mode = "auto"

        # Define an event handler object to process events in the system
        self.event_handler = EventHandler()
        self.bt_listener = BluetoothCommandListener(self.event_handler, self)

        # Enable the system if default_enabled is true
        if default_enabled:
            self.element.enabled = True
            self.element.apply_state()

        # Define sensor and damper management dictionaries
        self.room_sensors = dict()
        self.room_dampers = dict()

        # Define a temperature sensor for monitoring the temperature outside of the system to get an
        # indication on the temperature that the system is passively being set to
        self.external_temperature_sensor = TemperatureSensor(
            "external", system_constants.external_sensor_UUID["external"])

        # Define a temperature sensor for the output temperature
        # of the system that has been transferred from the heat exchanger
        self.temperature_output_sensor = TemperatureSensor(
            "out", system_constants.temperature_output_sensor_UUID["out"])

        # define ids for rooms
        room_ids = range(3)

        # Verify that all temperature sensors are connected to the bus
        connected_uuids = W1Bus()
        for _uuid in system_constants.sensor_UUIDS:
            if _uuid not in connected_uuids:
                system_logger.warning(f"The temperature sensor with ID: {_uuid} was unable to be located on the 1W-BUS")

        # self.servo_enabler = DeviceEnabler(system_constants.servo_enable_pin)

        # Setup dampers and sensors for each room
        for _id in room_ids:
            # todo: Gather target temperature
            self.room_sensors[_id] = TargetTemperatureSensor(
                _id=_id,
                _uuid=system_constants.sensor_UUIDS[_id],
                target_temperature=Temperature(system_constants.room_temp_targets[_id]))

            system_logger.info(f"Room {_id} target temp is: {self.room_sensors[_id].target_temp}")

            # Gather calibration data from constants file
            duty_deg_0, duty_deg_90, = system_constants.servo_duty_calibrations[_id]

            # Define the room dampers at the corresponding pin and min/max duty
            self.room_dampers[_id] = RegisterFlowController(
                _id=_id,
                pin=system_constants.room_servo_pins[_id],
                duty_at_deg0=duty_deg_0,
                duty_at_deg90=duty_deg_90,
            )
        self.room_readings = {}

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

    @property
    def bt_connection(self):
        return self.bt_listener.bt_connection

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

        :return: None
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
        Get a dictionary of the error values of sensors from a dictionary of readings

        :param readings: The list of readings to retrieve the errors from
        :return: A dictionary containing the {_id:error in deg C}
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
        external_temperature_readings, self.room_readings, element_sensor_readings = self.get_temperature_readings()

        # Create a dictionary to store all temperature errors
        room_error_readings = self.get_room_temperature_errors(room_readings)

        # Debugging code for now. todo: remove this for final testing
        print(room_error_readings)
        print(f"enabled: {self.element.enabled}\nheating: {self.element.heating}\ncooling: {self.element.cooling}")

        if self.mode == "auto":
            self.handle_auto_cycle(room_error_readings)
        elif self.mode == "test":
            pass
        elif self.mode == "extreme":
            self.handle_extreme_cycle(room_error_readings)

    def setup_test_mode(self):
        self.mode = "test"
        for room in self.room_sensors.values():
            room.target_temp = Temperature(22.5)

    def setup_auto_mode(self):
        self.mode = "auto"
        for room in self.room_sensors.values():
            room.target_temp = Temperature(22.5)

    def handle_auto_cycle(self, room_error_readings):
        # Iterate through each room
        for _id, servo in self.room_dampers.items():

            # Debugging code for now. todo: remove this for final testing
            print(f"room temperature delta: {room_error_readings[_id].celsius}")

            # If the system is currently heating/cooling
            if self.element.enabled:

                # If system in heating mode and the room temperature is still below the target
                if self.element.heating and (room_error_readings[_id].celsius >= 0.0):
                    servo.close_register()
                    print(f"System not heating room {_id}")

                # If system in cooling mode and the room temperature is still above the target
                elif self.element.cooling and (room_error_readings[_id].celsius <= 0.0):
                    servo.close_register()
                    print("System not cooling room")

                # The case if the temperature target has not been reached given the current system state
                else:
                    servo.open_register()

            # Dampers should be closed when the system is off
            else:
                servo.close_register()

        # Decide if the system should change temperature modes
        if self.error_sum(room_error_readings.values()) == 0.0:
            # Switch heating/cooling direction
            self.element.heating = self.element.cooling
            self.element.apply_state()

    def setup_extreme_mode(self):
        self.mode = "extreme"
        for room in self.room_sensors.values():
            room.target_temp = Temperature(22.5)

    def handle_extreme_cycle(self, room_error_readings):

        # Catch temperature in direction satisfied
        if self.error_sum(room_error_readings.values()) == 0.0:
            # Switch heating/cooling direction
            self.element.heating = self.element.cooling
            self.element.apply_state()

            # for room in self.room_sensors.values():
            self.room_sensors[0].target_temp += 0.1
            self.room_sensors[2].target_temp -= 0.1

    def error_sum(self, error_readings):
        """
        returns the sum of temperature error still needed to be satisfied in the system

        :param error_readings: An iterable of error readings to help decide the required target direction
        :return: None
        """
        # Define a error vector in out target temperature direction
        dir_error_total = 0.0

        # Now we need to decide if our current temperature target has been reached in the current temperature mode
        if self.element.heating:

            # Only cumulative readings in the target direction
            for e in error_readings:
                if e < 0.0:
                    dir_error_total += float(e)

        else:
            for e in error_readings:
                if e > 0.0:
                    dir_error_total += float(e)

        return dir_error_total

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
    sys = System(default_enabled=False)
