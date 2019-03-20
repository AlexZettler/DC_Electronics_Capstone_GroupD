import logging


class BTHandler(logging.Handler):

    """
    A logging handler for sending logged data to a bluetooth device
    """


    def __init__(self):
        super().__init__()
        pass

    def emit(self, record):
        self.acquire()


        self.release()

