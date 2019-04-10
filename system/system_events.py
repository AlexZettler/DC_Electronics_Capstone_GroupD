from event_system.events import *
from system.active_components import RegisterFlowController, DeviceEnabler
from system.sensors import TemperatureSensor
from system.sensors import TargetTemperatureSensor
from data_handling.data_classes import Temperature


class SystemEvent(Event):
    pass


class SystemStartEvent(SystemEvent):
    def __init__(self, element):
        self.element = element
        super().__init__()

    def action(self):
        self.element.enabled = True
        self.element.apply_state()


class SystemStopEvent(SystemEvent):
    def __init__(self, element):
        self.element = element
        super().__init__()

    def action(self):
        self.element.enabled = False
        self.element.apply_state()


class SystemOperationEvent(SystemEvent):
    pass


class SystemOperationModeTestEvent(SystemOperationEvent):
    def __init__(self, system):
        super().__init__()
        self.system = system

    def action(self):
        self.system.setup_test_mode()


class SystemOperationModeAutoEvent(SystemOperationEvent):
    def __init__(self, system):
        super().__init__()
        self.system = system

    def action(self):
        self.system.setup_auto_mode()


class SystemOperationModeExtremeEvent(SystemOperationEvent):
    def __init__(self, system):
        super().__init__()
        self.system = system

    def action(self):
        self.system.setup_extreme_mode()


class ElementEvent(Event):
    def __init__(self, element):
        super().__init__()
        self.element = element


class ElementHeatEvent(ElementEvent):
    def __init__(self, element):
        super().__init__(element)

    def action(self):
        self.element.heating = True


class ElementCoolEvent(ElementEvent):
    def __init__(self, element):
        super().__init__(element)

    def action(self):
        self.element.cooling = True


class ElementHeatAndCoolEvent(ElementEvent):
    def __init__(self, element):
        super().__init__(element)

    def action(self):
        self.element.enabled = False
        self.element.apply_state()


class ElementGetStatus(ElementEvent):
    def __init__(self, element, bt_server):
        super().__init__(element)
        self.bt_server = bt_server

    def action(self):
        # todo: set this up
        self.bt_server.send_string(self.element.heating)


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


class GetRoomTemperature(Event):
    def __init__(self, room_readings, sensor_id, bt_server):
        super().__init__()
        self.room_readings = room_readings
        self.sensor_id = sensor_id
        self.bt_server = bt_server

    def action(self):
        # todo: set this up
        temperature = self.system.room_readings[self.sensor_id]
        self.bt_server.send_string(temperature)


class FanEvent(Event):
    def __init__(self, fan: DeviceEnabler):
        super().__init__()
        self.fan = fan


class FanOnEvent(FanEvent):
    def __init__(self, fan: DeviceEnabler):
        super().__init__(fan)

    def action(self):
        self.fan.enable()


class FanOffEvent(FanEvent):
    def __init__(self, fan: DeviceEnabler):
        super().__init__(fan)

    def action(self):
        self.fan.disable()


class FanStatusEvent(FanEvent):
    def __init__(self, fan: DeviceEnabler, bt_server):
        super().__init__(fan)
        self.bt_server = bt_server

    def action(self):
        self.bt_server.send_string(self.fan.status)


