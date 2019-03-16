# This file contains class definitions for active components (system outputs)


# use https://pypi.org/project/PyBCM2835/
import RPi.GPIO as IO

from data_handling import custom_logger
import time

# Create a logger for general system information
system_logger = custom_logger.create_system_logger()

# Set Raspberry Pi pinout mode
IO.setmode(IO.BCM)


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

    def __init__(self, _room_id, peltier_heating, enabled: bool):
        super().__init__(_room_id=_room_id, target=0.0, p=0.0, i=0.0, d=0.0, b=0.0)
        self.heating = peltier_heating
        self.enabled = enabled

    @property
    def heating(self) -> bool:
        return self._heating

    @heating.setter
    def heating(self, val: bool):
        self._heating = val
        self._cooling = not val

    @property
    def cooling(self) -> bool:
        return self._heating

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
                # todo:  Set cooling pin low
                # todo:  Set heating pin high
            else:
                system_logger.info("Is now cooling")
                # todo:  Set heating pin low
                # todo:  Set cooling pin high

        else:
            system_logger.info("Is now disabled")
            # todo: Set heating pin low
            # todo: Set cooling pin low

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


class RegisterFlowController(object):
    # Constant PWM signal frequency
    freq = 50.0

    # Constant representing servo maximum turn rate
    turn_rate = 0.5

    # https://circuitdigest.com/microcontroller-projects/raspberry-pi-pwm-tutorial

    def __init__(self, _id, pin):
        # Sets the
        self._room_id = _id
        self._pin = pin

        self.logger = custom_logger.create_output_logger(_id)

        # todo: set channel up as an output
        ch = None
        self.last_pos = 0.0

        IO.setup(self._pin, IO.OUT)
        self.pwm_cont = IO.PWM(ch, self.freq)

        # start pwm controller with 0% duty cycle
        self.pwm_cont.start(0)
        self.set_to_pos(90.0)

    def set_to_pos(self, angle: float):
        # angle should be 0-180 degrees
        # Angle will only ever be set between 0 and 90 degrees in our case
        # 1/20 -> 1/10

        # Ensure that the angle is within the device limits
        if (angle >= 0.0) and (angle <= 180.0):

            # Calculate angle delta
            angle_delta = self.last_pos - angle

            # Verify that we are actually moving the servo motor
            if angle_delta != 0.0:
                # Generate a signal between (1 and 2)/20 of it's duty cycle
                duty_cycle = (1 + (angle / 180)) / 20

                # Change the PWM output to the calculated value
                self.pwm_cont.ChangeDutyCycle(duty_cycle)

                # Log the output
                self.logger.info(f"{angle}, {angle_delta}")

                # Store last position set so that the device doesn't need to rewrite an unchanged position
                self.last_pos = angle

        else:
            system_logger.debug(
                f"Device with id {id} tried to set it's position to '{angle}' which is outside of it's operating range")
