import time
import RPi.GPIO as GPIO
import math
import itertools
import math

servo_freq = 50

GPIO.setmode(GPIO.BCM)

# Setup servo
GPIO.setup(18, GPIO.OUT)
p = GPIO.PWM(18, servo_freq)  # channel=18 frequency=50Hz
p.start(0)

min_cycle = 0.45 / 20 * 100
max_cycle = 2.5 / 20 * 100

delta = max_cycle - min_cycle


def verify_pwm(duty_cycle: float):
    pass


class Servo(object):
    seconds_to_keep = 1.0
    pwm_freq = 50.0

    # In degrees per second
    angular_velocity = 90.0

    def __init__(self, pin: int, min_duty: float, max_duty: float):
        self.pin = pin

        self._min_duty = min_duty
        self._max_duty = max_duty

        self.angle_at_min_duty: float = None
        self.angle_at_max_duty: float = None

        # Setup PWM controller
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, self.pwm_freq)

        # Start the PWM controller
        self.start()

    def start(self):
        # Setup servo
        self.pwm.start(0)

    def stop(self):
        self.pwm.stop()

    def set_angle(self, angle):
        if not self.verify_angle(angle):
            raise ValueError(f"{angle} is outside of PWM controllers limits.")

        # Calculate deltas for y=mx+b formula
        delta_angle = self.angle_at_max_duty - self.angle_at_min_duty
        delta_duty = self.max_duty - self.min_duty

        angle_linear

    def verify_angle(self, angle):
        """
        Verifies that the desired angle is within the bounds of the PWM controller

        :param angle: The angle to test
        :return: Whether the angle is within the bounds
        """
        if self.angle_at_max_duty > angle > self.angle_at_min_duty:
            return True
        return False

    def apply_duty(self, duty: float):
        if verify_pwm(duty):
            self.pwm.ChangeDutyCycle(duty)
        else:
            print(f"{duty} is an invalid duty cycle!")

    @property
    def max_duty(self):
        return self.max_duty

    @max_duty.setter
    def max_duty(self, duty: float):
        if verify_pwm(duty):
            self._max_duty = duty
        else:
            print(f"{duty} is an invalid duty cycle!")

    @property
    def min_duty(self):
        return self._min_duty

    @min_duty.setter
    def min_duty(self, duty: float):
        if verify_pwm(duty):
            self._min_duty = duty

        else:
            print(f"{duty} is an invalid duty cycle!")

    def set_max_duty_angle(self, angle: float):
        self.angle_at_max_duty = angle

    def set_min_duty_angle(self, angle: float):
        self.angle_at_min_duty = angle

    def get_time_to_adjust(self, current_angle: float, target_angle: float):
        """
        Gets the time required to change the servo angle based on the angles given

        :param current_angle: The current angle that the PWM controller is set to
        :param target_angle: The angle that the PWM controller is set to change to
        :return: The time for the transition
        """
        delta_angle = math.fabs(current_angle - target_angle)
        time_to_change = delta_angle / self.angular_velocity
        return time_to_change

    def run_config(self):

        commands = {
            "start": self.start,
            "stop": self.stop,
            "set": self.apply_duty,
        }

        print(f"Valid commands are:n{'/n'.join(commands.keys())}")


try:
    p.ChangeDutyCycle(min_cycle)
    time.sleep(0.5)
    p.ChangeDutyCycle(max_cycle)
    time.sleep(0.5)

    while 1:
        res = 50
        servo_freq = 0.1
        sleep_time = 1 / 2 / res / servo_freq

        half_period_res = int(res / 2)

        for sin_resp in iter(
                delta * math.sin(x / res) for x in
                itertools.chain(range(0, half_period_res), range(half_period_res, 0, -1))):
            p.ChangeDutyCycle(min_cycle + sin_resp)
        time.sleep(sleep_time)

except KeyboardInterrupt:
    pass

p.stop()
GPIO.cleanup()
