from data_classes import Temperature, TemperatureReading
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
    def __init__(self, id, max_temp: Temperature, min_temp: Temperature):
        super().__init__(id)
        self.max_temp = max_temp
        self.min_temp = min_temp

    def get_temperature(self)->Temperature:
        current_temp = super().get_temperature()
        try:
            self.check_temperature_limits(current_temp)
        except OverTemperature:
            pass
        except UnderTemperature:
            pass

        return current_temp

    def check_temperature_limits(self, current_temp):
        if current_temp > self.max_temp:
            raise OverTemperature
        if current_temp < self.min_temp:
            raise UnderTemperature



class SystemMonitorController(object):
    def __init__(self, temperature_monitors: list):

        self.monitors = {}

        for monitor in temperature_monitors:
            self.monitors[monitor.id] = monitor

