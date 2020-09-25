import socket
import threading

HOST = '127.0.0.1'
PORT = 64444
MAX_PLAYERS = 4

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(MAX_PLAYERS)
server_socket.setblocking(False)


def accept_connection():
    try:
        conn, address = server_socket.accept()
        print(str(address) + " connected")
        conn_thread.start()
    except socket.error:
        pass


def receive():
    pass


def send():
    pass


conn_thread = threading.Thread(target=accept_connection(), args=(), daemon=True)
conn_thread.start()
recv_thread = threading.Thread(target=receive(), args=(), daemon=True)
recv_thread.start()
send_thread = threading.Thread(target=send(), args=(), daemon=True)
send_thread.start()


running = True
while running:
    pass
