from data_classes import Temperature, TemperatureReading

class TemperatureMonitor(object):
    def __init__(self, target_temperature: Temperature):
        self.target = target_temperature

    def temperature_updated(self, temperature: TemperatureReading):
        pass


class TemperatureMonitorController(object):
    def __init__(self, temperature_monitors: list):
        pass