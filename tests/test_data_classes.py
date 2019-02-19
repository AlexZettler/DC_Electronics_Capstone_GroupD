from data_handling import data_classes
import datetime


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

    test_inheritance(19.56)
    test_timestamp(19.56)


def test_Configuration():
    pass


def test_SystemConfiguration():
    pass


def test_RoomConfiguration():
    pass


def run_all():
    test_temperature()
    test_temperature_reading()
