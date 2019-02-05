import RPi.GPIO as IO

import custom_logger

# This file contains class definitions for active components (system outputs)


active_logger = custom_logger.create_measurement_logger()

#Set Raspberry Pi pinout mode
IO.setmode(IO.BCM)


class Element(object):

    def __init__(self, peltier_heating, enabled: bool):
        self.heating = peltier_heating
        self.enabled = enabled

    @property
    def heating(self)->bool:
        return self._heating

    @heating.setter
    def heating(self, val: bool):
        self._heating = val
        self._cooling = not val

    @property
    def cooling(self)->bool:
        return self._heating

    @cooling.setter
    def cooling(self, val: bool):
        self._cooling = val
        self._heating = not val

    @property
    def enabled(self)->bool:
        return self._enabled

    @enabled.setter
    def enabled(self, val: bool):
        self._enabled = val
        # Instantly disables the element if the enabled state is set False
        if val is False:
            self.apply_state()

    def apply_state(self):
        if self.enabled:
            if self.heating:
                active_logger.info("Is now heating")
                pass
                # Set cooling pin low
                # Set heating pin high
            else:
                active_logger.info("Is now cooling")
                # Set heating pin low
                # Set cooling pin high
                pass

        else:
            active_logger.info("Is now disabled")
            # Set heating pin low
            # Set cooling pin low
            pass

    def generate_new_target_vector(self, sensor_deltas: list)->None:
        # Generate a new target vector based on a pid controller

        p = sum(sensor_deltas)
        i = 0.0
        d = 0.0

        out_vector = sum((p,i,d))

        if out_vector > 0.0:
            self.heating = True

        if out_vector < 0.0:
            self.cooling = True

        if out_vector == 0.0:
            pass

class RegisterFlowController(object):
    freq = 50.0
    #https://circuitdigest.com/microcontroller-projects/raspberry-pi-pwm-tutorial
    def __init__(self, id, pin):
        self.id = id
        self._pin = pin

        ch=None
        self.last_pos = 0.0

        IO.setup(self._pin, IO.OUT)
        self.pwm_cont = IO.PWM(ch, self.freq)

        # start pwm controller with 0% duty cycle
        self.pwm_cont.start(0)
        self.set_to_pos(90.0)

    def set_to_pos(self, angle: float):
        #angle should be 0-180
        # 1/20 -> 1/10

        if (angle >=0.0) and (angle <=180.0):

            angle_delta = self.last_pos - angle

            if angle_delta != 0.0:


                duty_cycle = (1 + (angle / 180)) / 20

                self.pwm_cont.ChangeDutyCycle(duty_cycle)
                self.log_new_pos(angle)
                self.last_pos = angle

            else:
                pass
            # No change in position

        else:
            pass
            print("wtf willis")
            # this is critical and should be logged

    def log_new_pos(self, angle):
        active_logger.info(angle)