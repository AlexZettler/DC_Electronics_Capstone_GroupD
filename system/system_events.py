from event_system.events import *
from system.active_components import RegisterFlowController
from system.sensors import TemperatureSensor
from system.sensors import TargetTemperatureSensor
from data_handling.data_classes import Temperature

class ServoEvent(Event):
    pass


class RegisterEvent(ServoEvent):
    def __init__(self, register):
        self.register = register
        super().__init__()


class RegisterOpenEvent(RegisterEvent):
    def __init__(self, register: RegisterFlowController):
        super().__init__(register)

    def action(self):
        self.register.open_register()


class RegisterCloseEvent(RegisterEvent):
    def __init__(self, register: RegisterFlowController):
        super().__init__(register)

    def action(self):
        self.register.close_register()




class TemperatureTargetUpdatedEvent(Event):
    def __init__(self, target_sensor: TargetTemperatureSensor, new_target_value: Temperature):
        super().__init__()
        self.target_sensor = target_sensor
        self.new_target_value = new_target_value

    def action(self):
        self.target_sensor.target_temp = self.new_target_value


