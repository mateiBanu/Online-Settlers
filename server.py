import socket

HOST = '127.0.0.1'
PORT = 64444
MAX_PLAYERS = 4

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(MAX_PLAYERS)

while True:
    conn, address = server_socket.accept()
    print(address)
