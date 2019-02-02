import datetime
import json

class Temperature(object):
    def __init__(self, reading: float):
        self._reading = reading

    def __str__(self):
        return f"{self.celsius}C"

    def __repr__(self):
        return f"Temperature: {str(self)}"

    def __add__(self, other):
        return Temperature(self.celsius - other.celsius)

    def __sub__(self, other):
        return Temperature(self.celsius - other.celsius)

    def __gt__(self, other):
        return self.celsius > other.celsius

    def __lt__(self, other):
        return self.celsius < other.celsius

    @property
    def celsius(self)->float:
        return self._reading

    @celsius.setter
    def celsius(self, val: float):
        self._reading = val

    @property
    def fahrenheit(self)->float:
        return (self.celsius * 9/5) + 32

    @fahrenheit.setter
    def fahrenheit(self, val: float):
        self._reading = (val - 32) * 5/9


class TemperatureReading(Temperature):
    def __init__(self, reading: float):
        super().__init__(reading)
        self._timestamp = datetime.datetime.now()

    @property
    def timestamp(self)->datetime.datetime:
        return self._timestamp


class Configuration(object):

    def __init__(self, **kwargs):
        pass

    @property
    def _params(self)->dict:
        # Provide a property for json IO to interface with
        return dict()

    def to_json(self):
        return json.dumps(
            obj=self._params
        )

    @classmethod
    def from_json(cls, json_str:str):
        # Creates a Configuration instance from a given json string
        return cls(**json.loads(json_str))


class LimitConfiguration(Configuration):

    def __init__(self,max: float,min: float):
        self.max = max
        self.min = min
        super().__init__()

    @property
    def _params(self) -> dict:
        return {
            "max": self.max,
            "min": self.min
        }

class RoomConfiguration(Configuration):

    def __init__(self, ideal_temperature: float):
        self.ideal_temperature = ideal_temperature
        super().__init__()

    @property
    def _params(self)->dict:
        return {
            "ideal_temperature": self.ideal_temperature
        }

