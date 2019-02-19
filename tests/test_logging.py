import data_handling.custom_logger as cl
import data_handling.data_retrieval

import time


def test_measurement_logger():
    ml = cl.create_measurement_logger("dummy_id")

    ml.info("Dummy data 1")


    time.sleep(1.0)
    ml.info("Dummy data 2")

    time.sleep(1.0)
    ml.info("Dummy data 3")

    time.sleep(1.0)
    ml.info("Dummy data 4")

