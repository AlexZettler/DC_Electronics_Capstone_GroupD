import logging


class BTHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        pass

    def emit(self, record):
        self.acquire()


        self.release()

