"""
Event definition file
"""


class Event(object):
    param_name = None

    def __init__(self):
        pass

    def action(self):
        pass


class PrintEvent(Event):
    def __init__(self, what_to_print):
        self.what_to_print = what_to_print
        super().__init__()

    def action(self):
        print(self.what_to_print)


