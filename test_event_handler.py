import event_system.event_handler as eh
import event_system.events as events
import time

my_event_handler = eh.EventHandler()

my_event_handler.add_event(events.Event())
my_event_handler.add_event(events.PrintEvent("Hi"))

my_event_handler.add_event(events.PrintEvent("Hi"))

time.sleep(2.0)
print(my_event_handler.event_queue.empty())
