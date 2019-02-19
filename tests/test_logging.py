import data_handling.custom_logger as dl
import data_handling.data_retrieval as dr

import time


def test_measurement_logger():
    ml = dl.create_measurement_logger("dummy_id")

    ml.info("Dummy data 1")

    time.sleep(1.0)
    ml.info("Dummy data 2")

    time.sleep(1.0)
    ml.info("Dummy data 3")

    time.sleep(1.0)
    ml.info("Dummy data 4")

    readings = dr.iget_log_dirs()
