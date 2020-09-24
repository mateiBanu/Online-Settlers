import socket


class Clientconn:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.host = host
        self.port = port


class Serverconn:
    def __init__(self, host, port, connection_limit):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.host = host
        self.port = port
        self.socket.listen(connection_limit)


