"""
This file is a representation of the basic json format for our bluetooth api
This is not a REST api, as it is stateful and will only transmit when new data is introduced
"""
import json
import datetime

# Remember that the Pi is considered the server, and the tablet is considered the client

def server_to_client_transmission():
    """
    The Pi to tablet transmission data

    :return:
    """
    _obj = {
        "time": datetime.datetime.now(),
        "state": {

        }
    }
    return json.dumps(_obj)


def client_to_server_transmission():
    _obj = {
        "time": datetime.datetime.now(),
    }
    return json.dumps(_obj)
