import sys
import socket
import select
import pickle

BUFFERSIZE = 2048


server_addr = "127.0.0.1"
if len(sys.argv) == 2:
    serverAddr = sys.argv[1]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server_addr, 4321))

player_id = 0
name = input("Enter your name: ")

while True:
    ins, outs, ex = select.select([s], [], [], 0)
    for inm in ins:
        event = pickle.loads(inm.recv(BUFFERSIZE))
        if event[0] == "id update":
            player_id = event[1]
            s.send(pickle.dumps(["new", player_id, name]))
        # elif event[0] == "message":
        #     print(event[2])

    msg = input("Type a message: ")
    s.send(pickle.dumps(["message", player_id, msg]))

s.close()
