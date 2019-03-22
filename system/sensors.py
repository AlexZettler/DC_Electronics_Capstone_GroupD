from data_handling.data_classes import Temperature
from data_handling import custom_logger
from data_handling.custom_errors import OverTemperature, UnderTemperature

from glob import glob

# Create a logger to log general system information
system_logger = custom_logger.create_system_logger()


class TemperatureNotFound(Exception):
    """
    Represents a temperature taken form a DallasSensor object that could not be read
    """


class TemperatureSensor(object):
    """
    Base class for all temperature sensors.
    Implements methods for gathering data and logging results to unique log files
    """
    def __init__(self, _id, _uuid):
        # Assign the sensor an ID
        self._id = _id
        self.uuid = _uuid
        self._file_path = f"{W1Bus.BASE_DIR}28-{self.uuid}/w1_slave"

        # Create a logger for the sensor
        self.logger = custom_logger.create_measurement_logger(_id)

    def get_temperature(self) -> Temperature:
        """
        Retrieves measurement form the 1 wire interface and returns the results in degrees celsius
        Opens the device temperature reading file and retrieves the most recent temperature reading

        :return: The temperature read in degrees celsius
        """

        # Reads file until a proper reading found
        while True:

            # This should return the temperature reading
            lines = self.read_temp_raw()

            # checks if the last 3 characters in the file read "YES"
            if lines[0].strip()[-3:] == 'YES':
                break
            else:
                raise TemperatureNotFound

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

            # Log the retrieved temperature
            self.log_temperature(temp_c)

            # return the c degree float measurement of the temperature
            return Temperature(temp_c)

        else:
            # if "t=" was not found in the file
            raise TemperatureNotFound

    ###################
    #  Read Methods  #
    ###################
    def read_temp_raw(self):
        """
        Opens the device temperature reading file and retrieves all lines of the file
        """

        print(f"sensor id being read ID: {self._id}")

        # using the with open statement,
        # python will handle the closing of the file once it has broken from the with structure
        with open(self._file_path, 'r') as reading_file:
            # Reads the while file and returns a list of strings
            # Each element in the list is a part of the file separated with the "\n" character
            return reading_file.readlines()

    def log_temperature(self, temp_reading) -> None:
        """
        Log the measurement int the sensor's csv file

        :param temp_reading: The temperature reading to log to the csv file
        :return: None
        """

        self.logger.info(msg=temp_reading)


class TargetTemperatureSensor(TemperatureSensor):
    """
    A temperature sensor with a target temperature.
    This is used to model the rooms in the system.
    It is useful for calculating temperature target vectors6-
    """

    def __init__(self, _id, _uuid, target_temperature: Temperature):
        super().__init__(_id, _uuid)
        self.target_temp = target_temperature

    def temperature_error(self, temperature: Temperature):
        """
        Calculates the temperature delta from the target temperature

        :param temperature: The current temperature to calculate the delta from
        :return: The temperature delta
        """
        return temperature - self.target_temp


class ElementSensor(TemperatureSensor):
    """
    This is a class representing an element sensor.
    Because of the materials used, the element should never
    exceed specified temperature limits set in the constructor.
    """

    def __init__(self, _id, _uuid, max_temp: Temperature, min_temp: Temperature):
        super().__init__(_id, _uuid)
        self.max_temp = max_temp
        self.min_temp = min_temp

    def check_temperature_limits(self, current_temp) -> None:
        """
        This method should be called whenever the sensor is polled for data
        If the temperature exceeds the element limits it will raise a custom error

        :param current_temp: The current temp measured form the sensor
        :return: None
        """
        if current_temp > self.max_temp:
            system_logger.critical(f"Element turning off! {current_temp} is above it's limit of {self.max_temp} ")
            raise OverTemperature

        if current_temp < self.min_temp:
            system_logger.critical(f"Element turning off! {current_temp} is below it's limit of {self.min_temp} ")
            raise UnderTemperature


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
        self.extend(p[-12:] for p in glob(self.BASE_DIR + '28*'))

        # gets list of all folders matched with glob.glob, iterates through them
        # Strips the last 12 characters from all matched folders
        # Once ids are taken, reconstructs a list of these sensor IDs.

    def get_sensor_ids(self) -> list:
        """
        Getter method for sensor IDs
        Returns a list of 12 character long strings of the sensor ids
        """

        # return the entirety of the list
        return self
