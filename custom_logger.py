import logging

csv_formatter = logging.Formatter(
    fmt="%(asctime)s,%(levelname)s,%{message}s,",
    datefmt='%Y-%m-%d %H:%M:%S'
)

cons_formatter = logging.Formatter(
    fmt="%(asctime)s:%(levelname)s:%{message}s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

def create_measurement_logger(device_id):
    logger = logging.getLogger(f"measurement-{device_id}")
    logger.setLevel(logging.INFO)

    f_handler = logging.FileHandler(f"./log/measurements/{device_id}.csv")
    f_handler.setFormatter(csv_formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(cons_formatter)
    logger.addHandler(s_handler)

    return logger


def create_output_logger(device_id):
    logger = logging.getLogger(f"output-{device_id}")
    logger.setLevel(logging.INFO)

    f_handler = logging.FileHandler(f"./log/outputs/{device_id}.csv")
    f_handler.setFormatter(csv_formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(cons_formatter)
    logger.addHandler(s_handler)

    return logger


def create_system_logger():
    logger = logging.getLogger("system")
    logger.setLevel(logging.INFO)

    f_handler = logging.FileHandler("./log/system.csv")
    f_handler.setFormatter(csv_formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(cons_formatter)
    logger.addHandler(s_handler)

    return logger