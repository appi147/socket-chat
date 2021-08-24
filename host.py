import socket
import asyncore
import random
import pickle

BUFFERSIZE = 512

outgoing = []

id_client_map = {}


def update(message):
    arr = pickle.loads(message)
    command = arr[0]

    if command == "new":
        client_id = arr[1]
        name = arr[2]
        id_client_map[client_id] = name
    elif command == "message":
        client_id = arr[1]
        msg = arr[2]

        print(id_client_map)
        for i in outgoing:
            update = ['message']
            update.extend([client_id, f"{id_client_map[client_id]}: {msg}"])
            i.send(pickle.dumps(update))
            print('sent update data')


class Client:
    def __init__(self, id):
        self.id = id


class MainServer(asyncore.dispatcher):
    def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(10)

    def handle_accept(self):
        conn, addr = self.accept()
        print('Connection address:' + addr[0] + " " + str(addr[1]))
        outgoing.append(conn)
        id = random.randint(1000, 9999)
        conn.send(pickle.dumps(['id update', id]))
        SecondaryServer(conn)


class SecondaryServer(asyncore.dispatcher_with_send):
    def handle_read(self):
        recieved_data = self.recv(BUFFERSIZE)
        if recieved_data:
            update(recieved_data)
        else:
            self.close()


MainServer(4321)
asyncore.loop()
