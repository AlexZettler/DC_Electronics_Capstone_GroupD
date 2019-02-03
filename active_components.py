


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
        if val is False:
            self.apply_state()

        # Sets the correct pins high and low

    def apply_state(self):
        if self.enabled:
            pass

        else:
            return None
