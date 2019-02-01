import data_classes
import datetime

def run_all():
    test_temperature()
    test_temperature_reading()

def test_temperature():

    def test_units(_temp):
        test_temp = data_classes.Temperature(_temp)

        assert test_temp._reading == _temp
        assert test_temp.celsius == _temp

        assert test_temp.fahrenheit == 67.208

    def test_offset(_temp):
        test_temp = data_classes.Temperature(_temp)

        test_temp.celsius = -40.0
        assert test_temp.celsius == -40.0
        assert test_temp.fahrenheit == -40.0

        test_temp.fahrenheit = -40.0
        assert test_temp.celsius == -40.0
        assert test_temp.fahrenheit == -40.0


    test_units(19.56)
    test_offset(19.56)


def test_temperature_reading():

    def test_inheritance(_temp):
        test_temp = data_classes.TemperatureReading(_temp)
        assert isinstance(test_temp, data_classes.Temperature)


    def test_timestamp(_temp):
        test_temp = data_classes.TemperatureReading(_temp)
        assert test_temp.timestamp is test_temp._timestamp
        assert test_temp._timestamp.__class__ is datetime.datetime

    test_timestamp(19.56)


def test_Configuration():
    def verify_valid_params():
        assert data_classes.Configuration.valid_params == {}

    def no_params_on_empty_kwargs():
        conf = data_classes.Configuration()
        assert conf._params == {}

    def no_params_on_invalid_kwargs():
        conf = data_classes.Configuration(lol="koj")
        assert conf.valid_params == {}

    verify_valid_params()
    no_params_on_empty_kwargs()
    no_params_on_invalid_kwargs()


def test_SystemConfiguration():
    def verify_valid_params():
        assert data_classes.SystemConfiguration.valid_params.keys() == {
            "primary_max_temp",
            "primary_min_temp",
            "secondary_max_temp",
            "secondary_min_temp"
        }

    def no_params_on_empty_kwargs():
        conf = data_classes.Configuration()
        assert conf._params == {}

    def no_params_on_invalid_kwargs():
        conf = data_classes.Configuration(lol="koj")
        assert conf.valid_params == {}

    verify_valid_params()
    no_params_on_empty_kwargs()
    no_params_on_invalid_kwargs()

def test_RoomConfiguration():
    pass