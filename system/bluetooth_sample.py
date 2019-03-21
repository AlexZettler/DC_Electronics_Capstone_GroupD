import socket

recieve = False

if recieve:

    host_mac_address = '84:c7:ea:17:df:3d'

    port = 3

    backlog = 1

    size = 1024
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

    s.bind((host_mac_address,port))

    s.listen(backlog)

    try:
        client, address = s.accept()
        while True:
            data = client.recv(size)
            if data:
                print(data)
                client.send(data)
    except:
        print("Closing socket")
        client.close()
        s.close()
        
else:
    pass
    
    
    