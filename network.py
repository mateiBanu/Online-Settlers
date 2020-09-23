import socket

HOST = '127.0.0.1'
PORT = 64444

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))