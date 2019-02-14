from data_handling.data_classes import Temperature
from data_handling import custom_logger
from data_handling.custom_errors import OverTemperature, UnderTemperature

system_logger = custom_logger.create_system_logger()


class TemperatureSensor(object):
    """
    Base class for all temperature sensors
    """

    def __init__(self, _id):
        # Assign the sensor an ID
        self.id = _id

        # Create a logger for the sensor
        self.logger = custom_logger.create_measurement_logger(_id)

    def get_temperature(self)->Temperature:
        # todo: get the temperature reading
        temp_reading = None

        # Log the retrieved temperature
        self.log_temperature(temp_reading)
        return temp_reading

    def log_temperature(self, temp_reading):
        self.logger.info(msg=f"{self.id},{temp_reading}")

class TargetTemperatureSensor(TemperatureSensor):
    def __init__(self, _id, target_temperature: Temperature):
        super().__init__(_id)
        self.target_temp = target_temperature

    def calculate_temperature_delta(self, temperature: Temperature):
        return temperature - self.target_temp


class ElementSensor(TemperatureSensor):
    def __init__(self, id, max_temp: Temperature, min_temp: Temperature):
        super().__init__(id)
        self.max_temp = max_temp
        self.min_temp = min_temp

    def check_temperature_limits(self, current_temp):
        if current_temp > self.max_temp:
            system_logger.critical(f"Element turning off! {current_temp} is above it's limit of {self.max_temp} ")
            raise OverTemperature

        if current_temp < self.min_temp:
            system_logger.critical(f"Element turning off! {current_temp} is below it's limit of {self.min_temp} ")
            raise UnderTemperature