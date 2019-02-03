# This file contains class definitions for active components (system outputs)


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
                pass
                # Set cooling pin low
                # Set heating pin high
            else:
                # Set heating pin low
                # Set cooling pin high
                pass

        else:
            # Set heating pin low
            # Set cooling pin low
            pass

    def generate_new_target_vector(self, sensor_deltas: list)->None:
        #Generate a new target vector based on a pid controller

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


