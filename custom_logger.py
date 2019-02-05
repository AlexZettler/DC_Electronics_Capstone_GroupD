import logging


def create_measurement_logger():
    logger = logging.getLogger("measurement")
    logger.setLevel(logging.INFO)

    csv_formatter = logging.Formatter(
        fmt="%(asctime)s,%(levelname)s,%{message}s,",
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    cons_formatter = logging.Formatter(
        fmt="%(asctime)s:%(levelname)s:%{message}s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    f_handler = logging.FileHandler("./log/measurements.csv")
    f_handler.setFormatter(csv_formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(cons_formatter)
    logger.addHandler(s_handler)

    return logger

def create_output_logger():
    logger = logging.getLogger("output")
    logger.setLevel(logging.INFO)

    csv_formatter = logging.Formatter(
        fmt="%(asctime)s,%(levelname)s,%{message}s,",
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    cons_formatter = logging.Formatter(
        fmt="%(asctime)s:%(levelname)s:%{message}s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    f_handler = logging.FileHandler("./log/outputs.csv")
    f_handler.setFormatter(csv_formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler()
    s_handler.setFormatter(cons_formatter)
    logger.addHandler(s_handler)

    return logger

def create_system_logger():
    # A text based human readable log
    pass