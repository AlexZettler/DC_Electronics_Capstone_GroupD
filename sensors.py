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

    def get_target_temperature_delta(self):
        return self.get_temperature() - self.target_temp


class ElementMonitor(TemperatureSensor):
    def __init__(self, id, linked_element: Element, max_temp: Temperature, min_temp: Temperature):
        super().__init__(id)
        self.max_temp = max_temp
        self.min_temp = min_temp

        # Has a direct link to the element to be have the capability of disable
        # the element if an extreme temperature is detected.
        self.linked_element = linked_element

    def get_temperature(self)->Temperature:
        current_temp = super().get_temperature()
        try:
            self.check_temperature_limits(current_temp)

        except OverTemperature:
            # Should disable whatever temperature action that is taking place until the over condition is fixed
            self.linked_element.enabled = False
            self.log_temperature_extreme()

        except UnderTemperature:
            self.linked_element.enabled = False
            self.log_temperature_extreme()

        return current_temp

    def check_temperature_limits(self, current_temp):
        if current_temp > self.max_temp:
            raise OverTemperature
        if current_temp < self.min_temp:
            raise UnderTemperature

    def log_temperature_extreme(self):
        pass


