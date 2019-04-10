from bluetooth import *


# Referenced
#    http://pages.iu.edu/~rwisman/c490/html/pythonandbluetooth.htm
#    https://github.com/pybluez/pybluez/tree/master/examples/simple

class BT_Server(object):
    """
    A bluetooth server is a device which is responsible for managing the connection to client devices

    """

    def __init__(self):
        # Configure bluetooth socket_server
        self.server_socket = BluetoothSocket(RFCOMM)
        self.server_socket.bind(("", PORT_ANY))
        self.server_socket.listen(1)

        # Get the port that the socket_server it bound to
        self.port = self.server_socket.getsockname()[1]

        self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    def advertise_service(self):
        advertise_service(
            server_sock, "SampleServer",
            service_id=self.uuid,
            service_classes=[uuid, SERIAL_PORT_CLASS],
            profiles=[SERIAL_PORT_PROFILE],
            # protocols = [ OBEX_UUID ]
        )

    def stop_server(self):
        self.server_socket.close()
        self.client_socket.close()
        print("Server stopped")

    def wait_for_client(self):

        print(f"Waiting for connection on RFCOMM channel {self.port}")

        self.client_socket, self.client_info = self.server_socket.accept()
        print(f"Accepted connection from {self.client_info}")

    def recieve_data(self):

        try:
            while True:
                data = self.server_socket.recv(1024)
                if len(data) == 0: break
                print("received [%s]" % data)
        except IOError:
            self.client_disconnected()

    def send_string(self, _string):
        print("Transmission begun.")
        for p in break_string_into_segmented_byte_list(_string, None):
            self.client_socket.send(p)

        print("Transmission complete.")

    def client_disconnected(self):
        self.client_socket = None
        self.client_info = None
        self.client_socket.close()

        print("Client disconnected")


def break_string_into_segmented_byte_list(_string, packet_size=1024):
    """
    This doesn't even matter. There seems to be no limit on the maximum packet transmission size
    """

    # Turn the string into a btyes object
    byte_data = _string.encode()

    # If there is no packet length defined, send the entire bytes string in a single packet
    if packet_size is None:
        yield byte_data
        raise StopIteration

    # Get the number of bytes in the string
    byte_len = len(byte_data)

    # Get the number to packets to transmit
    number_of_packets = (byte_len // packet_size) + 1

    # Iterate through each packet and populate the packet_list
    for packet_num in range(number_of_packets):
        print(f"transmitting packet {packet_num}")
        _start = packet_num * packet_size
        _end = ((packet_num + 1) * packet_size) - 1
        try:
            # Return packet size of bytes
            yield byte_data[_start:_end]

        except KeyError:
            # If end could not be indexed, return the remainder of the bytes
            yield byte_data[_start:]

    raise StopIteration


if __name__ == "__main__":
    serv = BT_Server()
    serv.wait_for_client()

    serv.client_socket.recv(1024)

    trans_string = "\n".join((f"Lets go! {i}") for i in range(1024))
    serv.send_string(trans_string)
