import socket
import threading
import random
import pickle
import time
from message import *

HOST = '127.0.0.1'
PORT = 64444
MAX_PLAYERS = 4
player_count = 0
current_player = 0
players = []
started = False
board_setup = None

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Player:
    def __init__(self, conn, id):
        self.socket = conn
        self.id = id
        self.resources = [0, 0, 0, 0, 0, 0]
        self.devs = [0, 0, 0, 0, 0]
        self.points = 0

    def send(self, data):
        try:
            self.socket.send(pickle.dumps(data))
            return
        except socket.error as e:
            print(e)
            print("Failed to send to player " + str(self.id))

    def recv(self, size):
        while True:
            try:
                handle_message(pickle.loads(self.socket.recv(size)))
            except socket.error as e:
                pass

    def wait(self, size):
        ret = None
        while not ret:
            try:
                ret = self.socket.recv(size)
            except socket.error:
                pass
        return pickle.loads(ret)

    def add_res(self, new):
        for i in range(6):
            self.resources[i] += new[i]
        for p in players:
            p.send(Message(PAY_RES, self.id, new))

    def add_devs(self, new):
        for i in range(5):
            self.devs[i] += new[i]
        for p in players:
            p.send(Message(PAY_DEVS, self.id, new))


class Edge:

    def __init__(self, id):
        self.id = id
        self.owner = None
        self.full = False
        self.edges = []


class Intersection:

    def __init__(self, id):
        self.id = id
        self.owner = None
        self.level = 0
        self.edges = []


class Tile:

    def __init__(self, id):
        self.id = id
        self.resource = 0
        self.number = None
        self.robber = False
        self.inters = []


class Board:

    def __init__(self):
        dotrows = [3, 4, 4, 5, 5, 6, 6, 5, 5, 4, 4, 3]

        # Create intersections
        self.inters = []
        inter_id = 0
        for n in dotrows:
            l = [Intersection(inter_id)]
            inter_id += 1
            for j in range(n - 1):
                l.append(Intersection(inter_id))
                inter_id += 1
            self.inters.append(l)

        # Create edges
        self.edges = []
        edge_id = 0
        for i in range(11):
            l = []
            if dotrows[i] < dotrows[i + 1]:
                for j in range(dotrows[i]):
                    e = Edge(edge_id)
                    edge_id += 1
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i+1][j].edges.append(e)

                    e = Edge(edge_id)
                    edge_id += 1
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i + 1][j + 1].edges.append(e)
            if dotrows[i] == dotrows[i + 1]:
                for j in range(dotrows[i]):
                    e = Edge(edge_id)
                    edge_id += 1
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i + 1][j].edges.append(e)
            if dotrows[i] > dotrows[i + 1]:
                for j in range(dotrows[i + 1]):
                    e = Edge(edge_id)
                    edge_id += 1
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i + 1][j].edges.append(e)

                    e = Edge(edge_id)
                    edge_id += 1
                    l.append(e)
                    self.inters[i][j+1].edges.append(e)
                    self.inters[i + 1][j].edges.append(e)
            self.edges.append(l)

        # Create tiles
        self.tiles = []
        tile_id = 0
        deltas = [(0, 0), (1, 1), (2, 1), (3, 1), (2, 0), (1, 0)]
        for l in range(0, 4, 2):
            for i in range(dotrows[l]):
                t = Tile(tile_id)
                tile_id += 1
                for a, b in deltas:
                    t.inters.append(self.inters[l+a][i+b])
                self.tiles.append(t)
        l = 4
        deltas = [(0, 0), (1, 1), (2, 1), (3, 0), (2, 0), (1, 0)]
        for i in range(dotrows[l]):
            t = Tile(tile_id)
            tile_id += 1
            for a, b in deltas:
                t.inters.append(self.inters[l + a][i + b])
            self.tiles.append(t)
        deltas = [(0, 0), (1, 0), (2, 0), (3, -1), (2, -1), (1, -1)]
        for l in range(6, 10, 2):
            for i in range(1, dotrows[l]-1):
                t = Tile(tile_id)
                tile_id += 1
                for a, b in deltas:
                    t.inters.append(self.inters[l + a][i + b])
                self.tiles.append(t)

        self.edges = sum(self.edges, [])
        self.inters = sum(self.inters, [])

        for i in self.inters:
            for e in i.edges:
                for e2 in i.edges:
                    if e2 != e:
                        e.edges.append(e2)

    def update_tiles(self, v):
        robber, tiles = v
        for t in self.tiles:
            if t.id == robber:
                t.robber = True
            t.resource, t.number = tiles[t.id]

    def build_village(self, player, pos):
        self.inters[pos].owner = player
        self.inters[pos].level += 1
        for e in self.inters[pos].edges:
            e.full = True
        players[player].points += 1
        for p in players:
            p.send(Message(BUILD_VILLAGE, player, pos))

    def build_road(self, player, pos):
        self.edges[pos].owner = player
        for p in players:
            p.send(Message(BUILD_ROAD, player, pos))


board = Board()


def accept_connections():
    global player_count, board_setup
    while not started and player_count < MAX_PLAYERS:
        try:
            conn, address = server_socket.accept()
            print(str(address) + " connected")
            players.append(Player(conn, player_count))
            players[player_count].send((player_count, board_setup))
            player_count += 1
        except socket.error:
            pass


def init():
    print("Generating board...")
    res = [1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5]
    numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
    random.shuffle(res)
    random.shuffle(numbers)
    tiles = list(zip(res, numbers))
    tiles.insert(9, (0, 0))
    global board_setup
    board_setup = (9, tiles)
    board.update_tiles(board_setup)

    print("Initializing socket...")
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_PLAYERS)
        server_socket.setblocking(False)
    except socket.error as e:
        print(e)
    conn_thread = threading.Thread(target=accept_connections, args=())
    conn_thread.start()


def start():
    print("Starting game...")
    global started
    started = True
    for i in range(player_count):
        try:
            players[i].send(Message(INIT_VILLAGE, i, None))
            mess = players[i].wait(2048)
            board.build_village(mess.player, mess.data)
            players[i].send(Message(INIT_ROAD, i, mess.data))
            mess = players[i].wait(2048)
            board.build_road(mess.player, mess.data)
        except socket.error as e:
            print(e)
    for i in range(player_count-1, -1, -1):
        try:
            players[i].send(Message(INIT_VILLAGE, i, None))
            mess = players[i].wait(2048)
            board.build_village(mess.player, mess.data)
            players[i].send(Message(INIT_ROAD, i, mess.data))
            mess = players[i].wait(2048)
            board.build_road(mess.player, mess.data)
        except socket.error as e:
            print(e)
    for p in players:
        p.send(Message(START_TURN, 0, None))


def dice_roll():
    d1 = random.randint(1, 7)
    d2 = random.randint(1, 7)
    for p in players:
        p.send(Message(ROLL, current_player, (d1, d2)))
    player_res = [[0, 0, 0, 0, 0, 0] * player_count]
    for t in board.tiles:
        if t.number == d1 + d2:
            for i in t.inters:
                if i.owner is not None:
                    player_res[i.owner][t.resource] += i.level
    for p in players:
        for p2 in players:
            p.send(Message(PAY_RES, p2.id, player_res[p2.id]))


def handle_message(mess):
    if mess.flag == ROLL:
        dice_roll()
    elif mess.flag == BUILD_ROAD:
        board.build_road(mess.player, mess.data)
    elif mess.flag == BUILD_VILLAGE:
        board.build_village(mess.player, mess.data)
    elif mess.flag == PAY_RES:
        players[mess.player].add_res(mess.data)
    elif mess.flag == PAY_DEVS:
        players[mess.player].add_devs(mess.data)
    print("Got message with flag " + str(mess.flag))


def get_commands():
    while True:
        command = input()
        if command == "init":
            init()
        elif command == "start":
            start()
        elif command == "stop":
            print("Stopping...")


command_thread = threading.Thread(target=get_commands, args=())
command_thread.start()
