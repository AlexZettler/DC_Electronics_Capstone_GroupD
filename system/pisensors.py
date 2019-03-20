"""
TPRG2131
    Project 1: pisensors module
    Due: March 9, 2018

    Description:
        This project uses the raspberry pi as a sensor data collector and logger
        Main.py is the primary project file and references classes and functions defined here

Created by:
    Name: Alex Zettler
    E-Mail: alexander.zettler@dcmail.ca
    ID:100595682

Concepts:
    Source Control:
        This project uses fossil source control and requires check in and outs.
        The process to this begins with the initialization of a respitory:
            >fossil new [filename]

        To add files to the project:
            >fossil add [path to file/files]

        To create a new user:
            >fossil user new [username] [contact-info] [password]

        To open the respitory:
            >fossil open [filename] [username]

        To commit to the respitory:
            >fossil commit --user [username]

            -When commiting to the respitory, a file will be opened with notepad.
            -Add a commit message to the bottom of this file

        To close the respitory:
            >fossil close


    Polymorphism:
        Objects in this assignment use a parent object and therefore
        must call the parent's constructor using super().__init__(args)

        Objects that inherit a parent class inherit all attributes of the parent class
        Child classes override only the attributes redeclared

        Where attributes are class constants and methods
        (anything that an be called with cls.x where x is the attribute)
        

    Type hinting:
        In python 3.5 type hinting was added.

        Allows for the interpreter and developers to know what expected type of data
        should be passed into and out of functions if implemented properly

        Parameter type hinting is defined in a function declaration
        It is defined using:
            def funct(arg1: [type]):

        Return value type hinting is defined in a function declaration
        It is defined using:
            def funct()->[ret_type]:

        Together the call will look like:
            def funct(arg1: [type])->[ret_type]:
"""

#############
#  Imports  #
#############
import time
import datetime
import glob
import os

import math

import RPi.GPIO as GPIO

############################
#  Hardware Configuration  #
############################
GPIO.setmode(GPIO.BCM)

############################
#  Software Configuration  #
############################
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


#########################
#  Class deffinitions  #
#########################


class InvalidMeasurement(NotImplementedError):
    """
    Represents a reading that is not to be worked with
    """


class TemperatureNotFound(InvalidMeasurement):
    """
    Represents a temperature taken form a DallasSensor object that could not be read
    """


class Sensor(object):
    """
    Base class extended by all sensors.
    Allows a standard interface for accessing standard attributes of sensors

    Child classes must implement:
        _hardware_read
    """

    _SENSOR_TYPE = "generic"
    _UNITS = ""

    def __init__(self, sensor_name: str):
        self._name = str(sensor_name)

    ####################
    #  Getter Methods  #
    ####################
    def get_name(self):
        """Getter method for the name of the device"""
        return self._name

    @classmethod
    def get_type(cls):
        """
        Getter method for the type of device defined by the class

            Because the scope is only that of the class and is independent
            of individual instances of the class, therefore only needs to be a classmethod

            @classmethod defines this relationship
        """
        return cls._SENSOR_TYPE

    @classmethod
    def get_units(cls):
        """
        Getter method for the unit type defined by the class

            Because the scope is only that of the class and is independent
            of individual instances of the class, therefore only needs to be a classmethod

        @classmethod defines this relationship
        """
        return cls._UNITS

    ###################
    #  Read Methods  #
    ###################
    def read(self):
        """
        Get a measurement based on the current reading
        Pass all required object attributes to the constructor
        """
        return Measurement(self.get_name(), self._hardware_read(), self.get_units())

    def _hardware_read(self):
        """THIS IS AN ABSTRACT METHOD AND SHOULD NEVER BE CALLED"""
        raise InvalidMeasurement


class GPIOSensor(Sensor):
    """
    An abstract class that represents any sensor associated with a single GPIO header

    Child classes must implement:
        _hardware_setup 
        _hardware_read
    """

    def __init__(self, sensor_name: str, pin_number: int):
        """
        Constructor method for the abstract GPIOSensor class.

        Sets the:
            sensor name[str]:
                The name associated with the sensor,
                this should be human readable and unique to sensors

            pin_number[int]:
                The gpio pin to configure to the sensor.
        """

        # Initialize the parent Sensor object
        super().__init__(sensor_name)

        # Sets the pin number of the raspberry pi's GPIO header
        self._pin = int(pin_number)

        # calls the abstract method for a child class of the GPIOSensor
        # This means that this class will raise an error if it is not extended
        self._hardware_setup()

    def get_pin(self):
        return self._pin

    def _hardware_setup(self):
        raise NotImplementedError


class SwitchSensor(GPIOSensor):
    """
    This class is a representation of a switch and extends the GPIOSensor class.

    The sensor corresponds to a configured raspberry pi pin of the GPIO header
    The sensor will read a value based on the state of any boolean switch
    """

    # Define the sensor type class constant
    _SENSOR_TYPE = "switch"
    # Define the sensor unit class constant
    _UNITS = ""

    def __init__(self, sensor_name: str, pin_number: int, active_low: bool = False):
        """
        Constructor method for the SwithSensor class.

        Sets the:
            sensor name[str]:
                The name associated with the sensor,
                this should be human readable and unique to sensors

            pin_number[int]:
                The gpio pin to configure to the sensor.

            active low[bool]:
                Wheather to invert the reading of the GPIO pin
        """

        # Calls parent object constructor. In this case, the Sensor object
        # Feeds the sensor name so that the Sensor object can assign the _name object attribute
        super().__init__(sensor_name, pin_number)

        # if active low is set, inverts the reading of the device
        self._active_low = active_low

    def _hardware_setup(self) -> None:
        """
        Sets the pin set in the constructor as an input
        """

        GPIO.setup(self._pin, GPIO.IN)

    ###################
    #  Read Methods  #
    ###################
    def _hardware_read(self) -> bool:
        """
        #TODO Check if this returns a boolean or integer value
        This returns the logical state of the sensor

        :return: The value read by the push button
        """

        # The ^ is an exclusive or operator
        # This means that the output will be inverted if active_low is true
        return GPIO.input(self._pin) ^ self._active_low


class ResistiveSensor(GPIOSensor):
    """
    This class is a representation of a resistance measurement object
    It extends the GPIOSensor class.

    The sensor corresponds to a configured raspberry pi pin of the GPIO header
    Uses a charging capacitor to measure the time required to charge the pin to a HIGH reading.
    """

    _UNITS = "ohms"
    _SENSOR_TYPE = "RESISTIVE"

    # The voltage applied across the resistor being tested
    _VOLTAGE = 3.3

    # This is the voltage at which the RPi registers a HIGH reading
    _TRIGGER_VOLTAGE = 1.6

    # assume resistance between the GPIO header pin and ground through the RPi
    # this assumption must be made to calculate for the time required to discharge the capacitor

    _ASSUMED_DISCHARGE_RESISTANCE = 10.0

    def __init__(self, name: str, pin_number: int, capacitance: float):
        """
        Constructor method for the ResistiveSensor class.

        Sets the:
            sensor name[str]:
                The name associated with the sensor,
                this should be human readable and unique to sensors

            pin_number[int]:
                The gpio pin to configure to the sensor.

            capacitance[float]:
                The capacitance of the capacitor wired in the circuit in Ferads
        """

        # Both of these attributes will get set with hardware setup called in parent initializer
        self._discharge_time_const = None
        self._time_discharge_started = None

        # set the capacitance of the capacitor wired in the circuit
        self._capacitance = capacitance

        # configure as a GPIOSensor
        super().__init__(name, pin_number)

    def get_time_const(self, resistance) -> float:
        """
        Calculates and returns the time required to charge/discharge the capacitor
        The voltage is not exact and equils 99.3% of its maximum voltage
        """

        return 5.0 * resistance * self._capacitance

    def time_pin_charge(self) -> float:
        """
        Calculates the time required to read a high reading from the RPi GPIO pin
        """

        # calculate the amount of time since pin began discharging
        charge_time_delta = time.perf_counter() - self._time_discharge_started

        # calculate the diffence between the time waited and time for a full discharge
        wait_time = self._discharge_time_const - charge_time_delta

        # Waits the remaining time until the capacitor is fully discharged
        if wait_time > float(0):
            time.sleep(wait_time)

        start_time = time.perf_counter()
        GPIO.setup(self._pin, GPIO.IN)

        # Burn cpu cycles until the RPi reads a high reading
        while GPIO.output != GPIO.HIGH:
            pass

        # calculate the time it took to charge the capacitor
        time_delta = time.perf_counter() - start_time

        # Begins the pin discharge process before proceeding as there is no time delay
        self.begin_pin_discharge()

        # returns that period of time required to fully discharge the capacitor
        return time_delta

    def calculate_resistance(self) -> float:
        """
        Calculates the resistance of the resistor based on time required to charge the capacitor
        """

        # get the aount of time to charge the capacitor from the high voltage
        discharge_time = self.time_pin_charge()

        # calculate the resistance from the rc circuit charge formula
        return -discharge_time / self._capacitance / math.log(-self._TRIGGER_VOLTAGE / self._VOLTAGE - 1)

    def begin_pin_discharge(self) -> None:
        """
        This function is responsible for handling setting up a process to discharge the capacitor.
        In COMP lab#4 a static 200ms were waited until the capacitor was charged.
        This wait halts the entirety of the program and is not ideal.
        Instead we setup the pin and record the time when it was setup.
        When a reading is requested we wait any remaining time until the capacitor is discharged.
        """

        # Records the time when the discharge process began
        self._time_discharge_started = time.perf_counter()

        # Setup the discharging process
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin, GPIO.LOW)

    def _hardware_setup(self) -> None:
        """
        Override for parent GPIOSensor class
        Configures the sensor have a precofigured discharge time
        """

        # Calculate time constant 5(tau) based on the capacitance and resistance of the circuit
        self._discharge_time_const = self.get_time_const(
            self._ASSUMED_DISCHARGE_RESISTANCE)

        # Begin discharging the capacitor
        self.begin_pin_discharge()

    def _hardware_read(self) -> float:
        """
        An override method for the parent GPIOSensor
        retrieves the resistance of the load connected betwen the capacitor and the configured pin
        """

        return self.calculate_resistance()


class DallasTempSensor(Sensor):
    """
    This class is a representation of a temperature_sensor

    It uses the raspberry pi's 1 wire bus readings
    using a sensor specified by a given ID
    The sensor ID is used to parse a directory structure and return readings written to a file.
    """

    # Define the sensor type class constant
    _SENSOR_TYPE = "DallasTemperature"
    # Define the sensor unit class constant
    _UNITS = "C"

    def __init__(self, sensor_name: str, device_id: str):
        """
        Constructor method.

        Sets the:
            sensor name:
                The name associated with the sensor,
                this should be human readable and unique to sensors

            device_id:
                The unique 12 character long hex string found in the directory structure.
        """

        # Calls parent object constructor. In this case, the Sensor object
        # Feeds the sensor name so that the Sensor object can assign the _name object attribute
        super().__init__(sensor_name)

        # set the id of the sensor. This should be a 12 character long hex code
        self._id = device_id

        # Set variables to None initially because python likes to verify
        # that attributes have values before setting them with another method
        # and then set with the _hardware_setup() call
        self._file_path = None
        self._hardware_setup()

    ####################
    #  Getter Methods  #
    ####################
    def device_id(self) -> str:
        """
        Getter method for the device ID
        """
        return self._id

    def get_path(self) -> str:
        """
        Getter method for the path to the temperature reading
        """
        return self._file_path

    def _hardware_setup(self):
        """Configure the path based on a root directory and the device id"""
        self._file_path = "{0}28-{1}/w1_slave".format(
            W1Bus.get_base_directory(), self.device_id())

        # Attempt to open the sensor reading fil
        try:
            # Using the with open statement,
            # python will handle the closing of the file once it has broken from the with structure
            with open(self.get_path(), "r") as file_open_test:
                pass

        # If there was an issue opening the sensor file
        except:
            raise OSError

    ###################
    #  Read Methods  #
    ###################
    def read_temp_raw(self):
        """
        Opens the device temperature reading file and retrieves all lines of the file
        """

        # using the with open statement,
        # python will handle the closing of the file once it has broken from the with structure
        with open(self.get_path(), 'r') as reading_file:
            # Reads the while file and returns a list of strings
            # Each element in the list is a part of the file separated with the "\n" character
            return reading_file.readlines()

    def _hardware_read(self) -> float:
        """
        Overrides the base class(Sensor) object's method to return a measurement in degrees celsius
        Opens the device temperature reading file and retrieves the most recent temperature reading
        Returns a float that is the temperature reading in degrees celsius
        """

        # Reads file until a proper reading found
        while True:

            # This should return the temperature reading
            lines = self.read_temp_raw()

            # checks if the last 3 characters in the file read "YES"
            if lines[0].strip()[-3:] == 'YES':
                break
            else:
                time.sleep(0.2)

        # searches for "t=" in the temperature line that was found as the most recent measurement
        equals_pos = lines[1].find('t=')

        # If the value of t was found in the string
        if equals_pos != -1:

            # Pulls all values found after "t=" from the read string
            temp_string = lines[1][equals_pos + 2:]

            # Converts the retrieved string to a temperature reading
            temp_c = float(temp_string) / 1000.0

            # temp in ferenheight
            # temp_f = temp_c * 9.0 / 5.0 + 32.0

            # return the c degree float measurement of the temperature
            return temp_c

        else:
            # if "t=" was not found in the file
            raise TemperatureNotFound


class Measurement(object):
    """
    Represents a measurement taken
    When a read() function is called from a sensor, this object will be returned.
    This object takes attributes for the sensor and stores the time the measurement was taken.
    """

    def __init__(self, sensor_id: str, data, unit_name: str):
        """
        Create the Measurement object with the given sensor ID, data, and measurement unit
        """
        self._id = str(sensor_id).lower()
        self._data = data
        self._units = unit_name
        self._timestamp = datetime.time()

    ####################
    #  Getter Methods  #
    ####################
    def get_data(self):
        """getter method for the data stored in the object"""
        return self._data

    def get_units(self) -> str:
        """getter method for the name of the units stored in the object"""
        return self._units

    def get_posix_time(self) -> datetime.time:
        """getter method for the timestamp stored in the object"""
        return self._timestamp

    def get_timestamp(self) -> str:
        """string formatter method for self._timestamp"""
        return self._timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        """string formatter method for the measurement object"""
        return "<{}><{}><{}>{}".format(
            self._id, self._data, self._units, self.get_timestamp()
        )


class W1Bus(list):
    """
    The W1Bus object represents all currently loaded devices on the 1-Wire bus.

    The devices names are contained as a list of 12 character strings representing IDs
    """

    # Configure the path of devices on the 1-Wire device protocol
    BASE_DIR = "/sys/bus/w1/devices/"

    def __init__(self):
        """
        Gets all defined sensors and picks out the last 12 characters.
        This will match with the hex ID given to the sensor
        """

        # Creates the W1Bus as a child class of list
        super().__init__()

        # Adds all Sensors to the list
        self.extend(p[-12:] for p in glob.glob(self.BASE_DIR + '28*'))

        # gets list of all folders matched with glob.glob, iterates through them
        # Strips the last 12 characters from all matched folders
        # Once ids are taken, reconstructs a list of these sensor IDs.

    def get_sensor_ids(self) -> list:
        """
        Getter method for sensor IDs
        Returns a list of 12 character long strings of the sensor ids
        """

        # return the entirety of the list
        return self[:]

    @classmethod
    def get_base_directory(cls) -> str:
        """
        getter method for the W1 sensor base directory
        """
        return cls.BASE_DIR
