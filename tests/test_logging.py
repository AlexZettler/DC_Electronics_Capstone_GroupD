import data_handling.custom_logger as dl
import data_handling.data_retrieval as dr
import system.system_constants as sc

from types import GeneratorType as Generator
import logging
import os.path
import datetime


def test_logger():
    # for sensor_dir in dr.iget_log_dirs():
    #    for sensor_file in dr.iget_files_in_directory(sensor_dir, "csv"):
    #        pass
    def create_dummy_data():
        ml = dl.create_measurement_logger("dummy_id")
        assert isinstance(ml, logging.Logger)

        # Log some info
        ml.info("Dummy data 1")
        ml.info("Dummy data 2")
        ml.info("Dummy data 3")
        ml.info("Dummy data 4")

    create_dummy_data()


def test_retrieval():
    dummy_log_path = os.path.join(sc.base_log_directory, "measurements", "dummy_id.csv")

    def get_all_dummy_data():
        data_iterable = dr.iget_file_readings(dummy_log_path)

        # Confirm that the data retriever is a generator
        assert isinstance(data_iterable, Generator)
        data = [i for i in data_iterable]

        # Confirm that a list was created
        assert data is not None
        assert data

    def get_recent_dummy_data():
        data_iterable = dr.iget_deltatime_filtered_data(
            csv_file_path=dummy_log_path,
            time_delta=datetime.timedelta(seconds=2))

        # Confirm that the data retriever is a generator
        assert isinstance(data_iterable, Generator)

        # Confirm that data was gathered
        data = [i for i in data_iterable]

        # Confirm that a list was created
        assert data is not None
        assert data

        # Verify 4 data points were gathered
        assert len(data) == 4

    # Get all data from the log file
    get_all_dummy_data()

    # Get all recent data from the log file
    get_recent_dummy_data()


def run_all():
    test_logger()


if __name__ == '__main__':
    run_all()
