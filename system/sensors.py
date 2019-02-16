from data_handling.data_classes import Temperature
from data_handling import custom_logger
from data_handling.custom_errors import OverTemperature, UnderTemperature

# Create a logger to log general system information
system_logger = custom_logger.create_system_logger()


class TemperatureSensor(object):
    """
    Base class for all temperature sensors.
    Implements methods for gathering data and logging results to unique log files
    """

    def __init__(self, _id):
        # Assign the sensor an ID
        self.id = _id

        # Create a logger for the sensor
        self.logger = custom_logger.create_measurement_logger(_id)

    def get_temperature(self)->Temperature:
        """
        Retrieves measurement form the 1 wire interface and returns the results in degrees celsius
        :return: The temperature read in degrees celsius
        """

        # todo: get the temperature reading
        temp_reading = None

        # Log the retrieved temperature
        self.log_temperature(temp_reading)
        return temp_reading

    def log_temperature(self, temp_reading)->None:
        """
        Log the measurement int the sensor's csv file

        :param temp_reading: The temperature reading to log to the csv file
        :return: None
        """
        self.logger.info(msg=f"{self.id},{temp_reading}")

class TargetTemperatureSensor(TemperatureSensor):
    """
    A temperature sensor with a target temperature.
    This is used to model the rooms in the system.
    It is useful for calculating temperature target vectors
    """

    def __init__(self, _id, target_temperature: Temperature):
        super().__init__(_id)
        self.target_temp = target_temperature

    def temperature_error(self, temperature: Temperature):
        return temperature - self.target_temp


class ElementSensor(TemperatureSensor):
    """
    This is a class representing an element sensor.
    Because of the materials used, the element should never
    exceed specified temperature limits set in the constructor.
    """

    def __init__(self, id, max_temp: Temperature, min_temp: Temperature):
        super().__init__(id)
        self.max_temp = max_temp
        self.min_temp = min_temp

    def check_temperature_limits(self, current_temp)->None:
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
