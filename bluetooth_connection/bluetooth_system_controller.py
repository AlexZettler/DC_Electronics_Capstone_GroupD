"""
This file will eventually be responsible for instantiating a system controller object and managing state transfer between the bluetooth event handler and the system
"""

import multiprocessing as mp





def add_update_to_queue(q):
    q.put(BTSystemUpdate())


def wait_for_bluetooth_connection():
    pass


if __name__ == '__main__':
    mp.set_start_method('spawn')
    q = mp.Queue()

    try:
        while True:
            try:
                p = mp.Process(target=add_update_to_queue, args=(q,))
                p.start()
                print(q.get())
                p.join()

            except:
                pass

    except KeyboardInterrupt:
        pass
