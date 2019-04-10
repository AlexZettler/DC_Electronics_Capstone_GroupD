"""
This file is responsible for

"""

from threading import Thread, Lock
from queue import Queue

# from event_system.events import Event
from event_system.events import *


class EventHandler(object):
    def __init__(self):

        self._event_queue = Queue()
        self.event_handle_lock = Lock()
        # SetServoToDegree

    @property
    def event_queue(self):
        return self._event_queue

    def add_event(self, action: Event):
        """
        Add an action to the action queue and process it if another action is not currently being processed

        :param action: The action to handle
        :return: None
        """

        # Add the event to the queue
        self.event_queue.put(action)

        # Check if a thread is not currently processing the queue
        if not self.event_handle_lock.locked():
            self.process_event_queue()

    def process_event_queue(self):
        """
        Process actions until no more actions are in the queue
        :return: None
        """

        def event_handle_thread_function(obj: EventHandler):
            # Ensure that there are values in the queue
            while not obj._event_queue.empty():
                # Ensure that only one process is accessing the queue at a time
                obj.event_handle_lock.acquire()

                # Retrieve the new event
                _event = obj._event_queue.get()

                # Handle the event
                obj.event_handle(_event)

                # Indicate that the event handling has completed
                obj.event_handle_lock.release()

        # Define the thread
        event_thread = Thread(target=event_handle_thread_function, args=(self,))

        # Begin the thread
        event_thread.start()

    def event_handle(self, _event: Event):
        """
        An abstract method used to handle an event

        :param _event: The action to be processed
        :return: None
        """

        _event.action()
