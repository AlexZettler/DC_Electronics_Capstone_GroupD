from data_classes import Temperature, TemperatureReading
from active_components import Element

from custom_errors import OverTemperature, UnderTemperature


class TemperatureSensor(object):
    def __init__(self, _id):
        self.id = _id
        raise NotImplementedError

    def get_temperature(self)->Temperature:
        self.log_temperature()
        raise NotImplementedError

    def log_temperature(self):
        raise NotImplementedError


class TargetTemperatureSensor(TemperatureSensor):
    def __init__(self, _id, target_temperature: Temperature):
        super().__init__(_id)
        self.target_temp = target_temperature

    def calculate_temperature_delta(self, temperature: Temperature):
        return temperature - self.target_temp


class ElementMonitor(TemperatureSensor):
    def __init__(self, id, max_temp: Temperature, min_temp: Temperature):
        super().__init__(id)
        self.max_temp = max_temp
        self.min_temp = min_temp

    def check_temperature_limits(self, current_temp):
        if current_temp > self.max_temp:
            self.log_temperature_extreme(current_temp)
            raise OverTemperature

        if current_temp < self.min_temp:
            self.log_temperature_extreme(current_temp)
            raise UnderTemperature

    def log_temperature_extreme(self, current_temp):
        pass


