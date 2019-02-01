from data_classes import Temperature, TemperatureReading

class TemperatureMonitor(object):
    def __init__(self, target_temperature: Temperature):
        self.target_temp = target_temperature


    def temperature_updated(self, temperature: TemperatureReading):
        pass


class RoomMonitorController(object):
    def __init__(self, temperature_monitors: list):

        self.monitors = {}

        for id,monitor in zip(range(len(temperature_monitors)),temperature_monitors):
            self.monitors[id] = monitor



