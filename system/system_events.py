from event_system.events import *
from system.active_components import RegisterFlowController
from system.sensors import TemperatureSensor
from system.sensors import TargetTemperatureSensor
from data_handling.data_classes import Temperature


class SystemEvent(Event):
    pass


class SystemStartEvent(SystemEvent):
    pass


class SystemStopEvent(SystemEvent):
    pass


class SystemOperationEvent(SystemEvent):
    pass


class SystemOperationModeTestEvent(SystemOperationEvent):
    pass


class SystemOperationModeAutoEvent(SystemOperationEvent):
    pass


class SystemOperationModeExtremeEvent(SystemOperationEvent):
    pass


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


class RegisterRotateEvent(RegisterEvent):
    def __init__(self, register: RegisterFlowController, new_angle: float):
        super().__init__(register)
        self.new_angle = new_angle

    def action(self):
        self.register.rotate_to_angle(self.new_angle)


class RegisterPWMEvent(RegisterEvent):
    def __init__(self, register: RegisterFlowController, new_pwm: float):
        super().__init__(register)
        self.new_pwm = new_pwm

    def action(self):
        self.register.apply_duty(self.new_pwm)


class TemperatureTargetUpdatedEvent(Event):
    def __init__(self, target_sensor: TargetTemperatureSensor, new_target_value: Temperature):
        super().__init__()
        self.target_sensor = target_sensor
        self.new_target_value = new_target_value

    def action(self):
        self.target_sensor.target_temp = self.new_target_value
