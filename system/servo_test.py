import time
import RPi.GPIO as GPIO
import math
import itertools
import math

import data_handling.linear_interpolation as li

# servo_freq = 50

# Configure the Pinmode as BCM addressed pins
GPIO.setmode(GPIO.BCM)


# Setup servo
# GPIO.setup(18, GPIO.OUT)
# p = GPIO.PWM(18, servo_freq)  # channel=18 frequency=50Hz
# p.start(0)

# min_cycle = 0.45 / 20 * 100
# max_cycle = 2.5 / 20 * 100

# delta = max_cycle - min_cycle


class Servo(object):
    """
    Represents a servo capable of rotating a variable number of degrees
    """

    # The frequency of the PWM signal
    pwm_freq = 50.0

    # In degrees per second
    angular_velocity = 90.0

    # Represents tested limits of each of the servos
    pwm_limits = {
        "high": 1.0,
        "low": 0.0,
    }

    def __init__(self, pin: int, min_duty: float, max_duty: float):
        # Define the BCM pin to work with
        self.pin = pin

        # Create the angle duty cycle response line
        self.line = li.Line(
            x1=0.0,
            x2=90.0,
            y1=min_duty,
            y2=max_duty
        )

        # Setup PWM controller
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, self.pwm_freq)

        # Start the PWM controller
        self.start()

    @property
    def min_duty(self):
        return self.line.y1

    @property
    def max_duty(self):
        return self.line.y2


    def start(self):
        self.pwm.start(0)

    def stop(self):
        self.pwm.stop()

    def rotate_to_angle(self, angle: float) -> None:
        """
        Rotates the servo to a given degree

        :param angle: The angle to rotate the servo to
        :return: None
        """
        self.pwm.ChangeDutyCycle(self.get_angle_pwm(angle))

    def get_angle_pwm(self, angle: float) -> float:
        """
        Retrieves the pwm duty cycle from an angle based on a line drawn between two points

        :param angle: The angle to retrieve the PWM signal for
        :return: The pwm duty cycle at the given angle
        """
        #if not self.verify_angle(angle):
        #    raise ValueError(f"{angle} is outside of PWM controllers limits.")
        return self.line[angle]

    def verify_pwm_within_limits(self, pwm: float) -> bool:
        """
        Verifies that the pwm to send to the servo is within the allowable limits

        :param pwm: The pwm value to check
        :return: boolean representing if the pwm passed in is within the limits
        """
        result = self.pwm_limits["high"] > pwm > self.pwm_limits["low"]
        assert isinstance(result, bool)
        return result

    def apply_duty(self, duty: float):
        if self.verify_pwm_within_limits(duty):
            self.pwm.ChangeDutyCycle(duty)
        else:
            print(f"{duty} is an invalid duty cycle!")

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

        # Define the main commands of the program
        commands = {
            "start": self.start,
            "stop": self.stop,
            "set": self.apply_duty,
            "exit": None
        }

        # Enter a null response
        response = ""

        while response not in commands.keys():
            print(f"Valid commands are:n{'/n'.join(commands.keys())}")
            response = input("Please enter a command: ").lower()

        if response == "exit":
            pass
        elif response == "set_duty":
            kwargs = {}

            duty_user_resp = float(input("Please enter a duty cycle: "))
            kwargs["duty"] = duty_user_resp
            commands[response](**kwargs)

        else:
            commands[response]()

    def sin_response(self, resolution, response_freq):
        sleep_time = 1 / 2 / resolution / response_freq

        half_period_res = int(resolution / 2)

        delta = self.max_duty - self.min_duty

        # Define an iterable to model a triangle wave with 50% duty cycle
        response = itertools.chain(range(0, half_period_res), range(half_period_res, 0, -1))

        # Iterate through each
        for sin_resp in iter(delta * math.sin(x / resolution) for x in response):
            print(sin_resp)
            self.pwm.ChangeDutyCycle(self.min_duty + sin_resp)

            # Wait whatever time dictated by resolution
            time.sleep(sleep_time)


if __name__ == '__main__':
    s = Servo(18, 0.45/20, 2.5/20)
    s.rotate_to_angle(90.0)
    time.sleep(1.0)
    s.rotate_to_angle(0.0)


