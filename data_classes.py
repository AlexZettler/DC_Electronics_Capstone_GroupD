import datetime
import json

class Temperature(object):
    def __init__(self, reading: float):
        self.celsius = reading
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


class Configuration():
    #A dictionary containing dictionary keys and the expected value type
    valid_params = {
        "primary_max_temp":float,
        "primary_min_temp": float,
        "secondary_max_temp": float,
        "secondary_min_temp": float,
    }

    def __init__(self, **kwargs):

        #Construct a parameter dictionary
        self.params = {k: v for k,v in kwargs.items() if (
                k in self.valid_params.keys() and
                type(v)is self.valid_params[k]
            )
        }

    def to_json(self):
        return json.dumps(
            obj=self.params
        )

    @classmethod
    def from_json(cls, json_str:str):
        #Creates a Configuration instance from a given json string
        return cls(**json.loads(json_str))



