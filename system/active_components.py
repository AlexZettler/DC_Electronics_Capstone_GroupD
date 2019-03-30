# This file contains class definitions for active components (system outputs)


# use https://pypi.org/project/PyBCM2835/
import RPi.GPIO as GPIO

from data_handling import custom_logger
import time
from system.system_constants import heating_pin, cooling_pin
import data_handling.linear_interpolation as li
import math
import itertools

# Create a logger for general system information
system_logger = custom_logger.create_system_logger()

# Set Raspberry Pi pinout mode
GPIO.setmode(GPIO.BCM)


class OutputController(object):
    def __init__(self, _id):
        self._room_id = _id


class PID(OutputController):
    # Based loosely on: https://github.com/ivmech/ivPID/blob/master/PID.py
    """
    A class representing a PID interface for a device
    """

    def __init__(self, _room_id, target, p, i, d, b):
        # Sets output id
        super().__init__(_room_id)

        # Set a target to compare error against
        self.target = target

        # Define P,I,D, and b parameters
        self._p = p
        self._i = i
        self._d = d
        self._b = b

        # Set cumulative i to non to verify that reset works properly
        self.cumulative_i = None
        self.reset_integral()

        # Define attributes of the last value read
        self.last_meas_time = None
        self.last_meas_error = None

    def get_update_vector(self, current_measurement) -> float:
        # Get the current time
        current_time = time.time()

        # Calculate current error
        current_error = current_measurement - self.target

        # Handle start condition where the last measurement was not gathered
        if (self.last_meas_time is None) or (self.last_meas_error is None):
            self.last_meas_time, self.last_meas_error = current_time, current_error

            # Without a delta time the P portion is the only portion of term that can be returned
            return self.get_p_term(current_error)

        # Calculate the time and error deltas since last reading
        delta_time = current_time - self.last_meas_time
        delta_error = current_error - self.last_meas_error

        # todo: Windup guard is a thing to worry about

        # Add the current error to the running integral term
        self.update_cumulative_i_term(delta_error, delta_time)

        # todo: log this to a debug log

        # Store the current time for next reading
        self.last_meas_time = current_time

        # Define the terms to take into consideration
        terms = (
            self.get_p_term(current_error),
            self.get_i_term(),
            self.get_d_term(delta_error, delta_time),
            self._b
        )

        # Return the sum of terms
        return sum(terms)

    ########################
    # Proportional methods #
    ########################
    def get_p_term(self, error: float):
        """
        Pure function for calculating the p term

        :param error:
        :return:
        """
        return self._p * error

    ####################
    # Integral methods #
    ####################
    def reset_integral(self):
        self.cumulative_i = 0.0

    def update_cumulative_i_term(self, delta_error, delta_time):
        self.cumulative_i += delta_error * delta_time

    def get_i_term(self):
        return self._i * self.cumulative_i

    ######################
    # Derivative methods #
    ######################
    def get_d_term(self, delta_error, delta_time):
        return delta_error / delta_time


class Element(PID):

    def __init__(self, _room_id, peltier_heating):
        super().__init__(_room_id=_room_id, target=0.0, p=0.0, i=0.0, d=0.0, b=0.0)

        GPIO.setup(heating_pin, GPIO.OUT)
        GPIO.setup(cooling_pin, GPIO.OUT)

        self.heating = peltier_heating
        self.enabled = False

    @property
    def heating(self) -> bool:
        return self._heating

    @heating.setter
    def heating(self, val: bool):
        self._heating = val
        self._cooling = not val

    @property
    def cooling(self) -> bool:
        return not self._heating

    @cooling.setter
    def cooling(self, val: bool):
        self._cooling = val
        self._heating = not val

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, val: bool):
        self._enabled = val
        # Instantly disables the element if the enabled state is set False
        if val is False:
            self.apply_state()

    def apply_state(self) -> None:
        """
        Sets the pins of the Raspberry PI to apply the current heat/cool and enabled state.
        This is a software safety method and verifies that pins are enabled and disabled in the correct order.

        :return: None
        """
        if self.enabled:
            if self.heating:
                system_logger.info("Is now heating")
                GPIO.output(cooling_pin, False)
                GPIO.output(heating_pin, True)

            else:
                system_logger.info("Is now cooling")
                GPIO.output(heating_pin, False)
                GPIO.output(cooling_pin, True)

        else:
            system_logger.info("Is now disabled")
            GPIO.output(heating_pin, False)
            GPIO.output(cooling_pin, False)

    def generate_target_vector(self, main_temp, sensor_deltas: dict) -> None:
        """
        Generate a new target vector based on a pid controller

        :param main_temp:
        :param sensor_deltas:
        :return:
        """

        # out_vector = self.update_with_values()

        # todo: implement PID controller
        out_vector = sum(sensor_deltas.values())

        if out_vector > 0.0:
            self.heating = True

        if out_vector < 0.0:
            self.cooling = True

        if out_vector == 0.0:
            pass


class Servo(object):
    """
    Represents a servo capable of rotating a variable number of degrees
    """

    # The frequency of the PWM signal
    pwm_freq = 50.0

    # In degrees per second
    angular_velocity = None

    # Represents tested limits of each of the servos
    pwm_limits = {
        "high": 2.50,
        "low": 0.45,
    }

    def __init__(self, pin: int, min_duty: float, max_duty: float):
        # Define the BCM pin to work with
        self._pin = pin

        # Create the angle duty cycle response line
        self.line = li.Line(
            x1=0.0,
            x2=90.0,
            y1=max_duty,
            y2=min_duty
        )

        # Setup PWM controller
        GPIO.setup(self._pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self._pin, self.pwm_freq)

        # Start the PWM controller
        self.start()

    @property
    def pin(self):
        return self._pin

    @property
    def min_duty(self):
        return self.line.y1

    @property
    def max_duty(self):
        return self.line.y2

    def start(self):
        self.pwm.start(self.min_duty)

    def stop(self):
        self.pwm.stop()

    #def __del__(self):
    #    GPIO.cleanup(self.pin)

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
        # if not self.verify_angle(angle):
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


class RegisterFlowController(Servo):
    # Todo: merge servo test into this class, as it is a more robust solution

    # Constant PWM signal frequency
    pwm_freq = 50.0

    # Constant representing servo maximum turn rate in deg/sec
    angular_velocity = 360.0

    # https://circuitdigest.com/microcontroller-projects/raspberry-pi-pwm-tutorial

    def __init__(self, _id, pin, min_duty, max_duty):
        # Creates the parent servo object
        super().__init__(pin=pin, min_duty=min_duty, max_duty=max_duty)

        self.logger = custom_logger.create_output_logger(_id)


    def rotate_to_angle(self, angle: float) -> None:
        """
        Rotates the servo to a given degree

        :param angle: The angle to rotate the servo to
        :return: None
        """
        self.logger.info(f"{angle}")
        super().rotate_to_angle(angle)
