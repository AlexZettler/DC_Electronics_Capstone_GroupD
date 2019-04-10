# This file contains class definitions for active components (system outputs)


# use https://pypi.org/project/PyBCM2835/
import RPi.GPIO as GPIO

from data_handling import custom_logger
import time
from system.system_constants import heating_pin, cooling_pin
import data_handling.linear_interpolation as li
import math
import itertools
from queue import Queue

# Create a logger for general system information
system_logger = custom_logger.create_system_logger()

# Set Raspberry Pi pinout mode
GPIO.setmode(GPIO.BCM)
from threading import Thread, Lock


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


class Element(object):

    def __init__(self, peltier_heating):
        super().__init__()

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

    @property
    def cooling(self) -> bool:
        return not self._heating

    @cooling.setter
    def cooling(self, val: bool):
        self._heating = not val

    @property
    def get_heating_mode_string(self):
        enabled_str = {
            True: "Enabled",
            False: "Disabled"
        }[self.enabled]
        heatmode_str = {
            True: "Heating",
            False: "Cooling"
        }[self.heating]
        return f"{enabled_str} {heatmode_str}"

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


    def handle_element_disable_state_toggle(self):
        def action_handler(element: Element):
            while True:
                if element.enabled:

                else:
                    if element.heating
                    GPIO.output(heating_pin, False)

        t = Thread(target=action_handler)
        t.start()


    def generate_target_vector(self, main_temp, sensor_deltas: dict) -> None:
        """
        Generate a new target vector based on a pid controller

        :param main_temp:
        :param sensor_deltas:
        :return:
        """

        # out_vector = self.update_with_values()

        # todo: implement PID controller
        # out_vector = sum(sensor_deltas.values())

        all_rooms_satisfied = True
        for td in sensor_deltas.values():

            # If any rooms are below the target temperature when they are in heating mode
            if self.heating:
                if td < 0.0:
                    # Switch the default condition and stop iterating
                    all_rooms_satisfied = False
                    break

            # If any rooms are above the target temperature when they are in cooling mode
            else:
                if td > 0.0:
                    # Switch the default condition and stop iterating
                    all_rooms_satisfied = False
                    break

        if all_rooms_satisfied:
            new_mode_name = {
                True: "heating",
                False: "cooling"
            }[not self.heating]

            system_logger.info(f"All rooms have reached their target temperature, switching to {new_mode_name} mode")
            self.heating = self.cooling


class ServoPWMDispatcher(object):
    pwm_freq = 50.0
    servo_deg_per_sec = 90.0
    """
    Do not use!
    """

    def __init__(self, pwm_pin: int, control_pins: dict, pwm_scaling):
        # Define the BCM pin to work with
        self._pin = pwm_pin

        # Store the pins that each room's servo is enable/controlled with
        self._control_pins = control_pins

        # Define angle to pwm scaling lines
        self.room_pwm_lines = {}

        # Set servo calibrations
        for _id in self._control_pins.keys():
            duty_at_deg0, duty_at_deg90 = pwm_scaling[_id]

            # Create the angle duty cycle response line
            self.room_pwm_lines[_id] = li.Line(
                x1=0.0,
                x2=90.0,
                y1=duty_at_deg0,
                y2=duty_at_deg90
            )

        # Define average pwm signals for initial calibration
        avg_0deg_pwm = sum(device[0.0] for device in self.room_pwm_lines.values()) / len(self.room_pwm_lines)
        avg_90deg_pwm = sum(device[90.0] for device in self.room_pwm_lines.values()) / len(self.room_pwm_lines)

        for _id, cp in self._control_pins.items():
            # Setup each servo enable pin as an output and pull the pin low
            GPIO.setup(cp, GPIO.OUT)
            GPIO.output(cp, False)

        # Setup PWM controller
        GPIO.setup(self._pin, GPIO.OUT)

        print(f"My channel is {self._pin}")
        self.pwm = GPIO.PWM(self._pin, self.pwm_freq)

        # Define a command queue for the multiplexed controller
        self.cmd_queue = Queue()

        # reset positions of each device
        self._servo_positions = {k: 0.0 for k in self._control_pins}
        self.set_all_rooms_to_pwm(avg_0deg_pwm)

        for _id, _pin in self._control_pins.items():
            self.add_room_to_deg_to_queue(_id, 0.0)

        # Create the action handler thread
        self.setup_action_handle_thread()

    def set_all_rooms_to_pwm(self, duty: float):
        """
        Sets all room servos to a given PWM duty
        :param duty: The duty to set room servos to
        :return:
        """
        for pin in self._control_pins.values():
            GPIO.output(pin, True)

        print(f"Changing all channels to {duty}")

        # Reset all servos to an averaged
        self.pwm.ChangeDutyCycle(duty)
        _delay_time = 180.0 / self.servo_deg_per_sec
        print(f"sleeping for {_delay_time}")
        time.sleep(_delay_time)

        for pin in self._control_pins.values():
            GPIO.output(pin, False)

    # def add_action_to_queue(self, action: Event):
    #    self.cmd_queue.put(action)

    def setup_action_handle_thread(self):
        pass
        """
        Set up a thread to handle new room rotation events
        """
        #
        # def thread_loop(obj: ServoPWMDispatcher):
        #     while True:
        #         if not self.cmd_queue.empty():
        #
        #             # Retrieve new action parameters
        #             action = self.cmd_queue.get()
        #             if isinstance(SetServoToDegree):
        #
        #
        #
        #             print(f"Processing new command with arguments {mode}, {room_id}, {param}")
        #
        #             # Enable the pwm line that is being worked with
        #             GPIO.output(obj._control_pins[int(room_id)], True)
        #
        #             if mode == "angle":
        #
        #                 _duty_cycle = obj.room_pwm_lines[room_id][param]
        #                 print(f"rotating to angle: {param} with duty: {_duty_cycle}")
        #                 # Set PWM output to the degree measure
        #                 obj.pwm.ChangeDutyCycle(_duty_cycle)
        #
        #                 # Wait period of time for servo to transition
        #                 angle_delta = math.fabs(obj._servo_positions[room_id] - param)
        #                 expected_transition_time = angle_delta / obj.servo_deg_per_sec
        #                 print(f"sleeping {expected_transition_time}")
        #                 time.sleep(expected_transition_time)
        #
        #                 # Store new position
        #                 self._servo_positions[room_id] = param
        #
        #             elif mode == "duty":
        #
        #                 # Set PWM output
        #                 obj.pwm.ChangeDutyCycle(param)
        #
        #                 # Wait period of time for servo to transition
        #                 expected_transition_time = 180 / obj.servo_deg_per_sec
        #                 print(f"sleeping {expected_transition_time}")
        #                 time.sleep(expected_transition_time)
        #
        #             else:
        #                 system_logger.warning(f"Action handle thread was passed an invalid command with mode {mode}")
        #
        #             # Enable the pwm line that is being worked with
        #             GPIO.output(obj._control_pins[int(room_id)], False)
        #
        #         else:
        #             time.sleep(0.5)
        #
        # servo_action_thread = Thread(
        #     target=thread_loop,
        #     args=(self,)
        # )
        # servo_action_thread.start()


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
        "high": 25.0,
        "low": 4.5,
    }

    def __init__(self, pin: int, duty_at_deg0: float, duty_at_deg90: float):
        # Define the BCM pin to work with
        self._pin = pin

        # Create the angle duty cycle response line
        self.line = li.Line(
            x1=0.0,
            x2=90.0,
            y1=duty_at_deg0,
            y2=duty_at_deg90
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

    # def __del__(self):
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
        # if self.verify_pwm_within_limits(duty):
        self.pwm.ChangeDutyCycle(duty)
        # else:
        # print(f"{duty} is an invalid duty cycle!")

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

    def __init__(self, _id, pin, duty_at_deg0: float, duty_at_deg90: float):
        # Creates the parent servo object
        super().__init__(
            pin=pin,
            duty_at_deg0=duty_at_deg0,
            duty_at_deg90=duty_at_deg90)

        self.logger = custom_logger.create_output_logger(_id)

    def rotate_to_angle(self, angle: float) -> None:
        """
        Rotates the servo to a given degree

        :param angle: The angle to rotate the servo to
        :return: None
        """
        self.logger.info(f"{angle}")
        super().rotate_to_angle(angle)

    def open_register(self):
        self.rotate_to_angle(0.0)

    def close_register(self):
        self.rotate_to_angle(90.0)


class DeviceEnabler(object):
    """
    A device responsible for handling device control
    """

    def __init__(self, pin):
        self.pin = pin

        GPIO.setup(self.pin, GPIO.OUT)
        self.status = False
        GPIO.output(self.pin, False)

    def enable(self):
        self.status = True
        GPIO.output(self.pin, True)

    def disable(self):
        self.status = False
        GPIO.output(self.pin, False)

    def time_enable(self, _time: float):
        def thread_action(obj: DeviceEnabler):
            obj.enable()
            time.sleep(_time)
            obj.disable()

        servo_enable_thread = Thread(
            target=thread_action,
            args=(self,)
        )
        servo_enable_thread.start()

    def time_disable(self, _time: float):
        def thread_action(obj: DeviceEnabler):
            obj.disable()
            time.sleep(_time)
            obj.enable()

        servo_enable_thread = Thread(
            target=thread_action,
            args=(self,)
        )
        servo_enable_thread.start()
