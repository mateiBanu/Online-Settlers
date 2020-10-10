import pygame
import os
import sys
import math
import socket
import random
import pickle
import threading
from message import *

WIDTH = 1024
HEIGHT = 768
CAPTION = "Online Settlers"

BACK_COLOR = (0, 222, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (252, 219, 3)
ORANGE = (255, 128, 0)
LIME = (51, 255, 51)
DARK_GREEN = (0, 102, 0)
GREY = (128, 128, 128)
WHITE = (245, 244, 237)

enabled_buttons = []

# Sizes for hex geometry
L = 80
A = int(L/2)
B = int(A * math.sqrt(3))

# Initialize pygame and create window
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(CAPTION)
pygame.font.init()
tile_font = pygame.font.SysFont("arial", 30)
build_font = pygame.font.SysFont("arial", 12)

clock = pygame.time.Clock()


def data(s):
    return "imgs/" + s


def dist(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


beep_counter = 0


def beep():
    global beep_counter
    beep_counter += 1
    print("BEEP! " + str(beep_counter))


class Network:

    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 64444
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        data = None
        try:
            self.socket.connect((self.host, self.port))
        except socket.error:
            print("Connection error")
            done()
        try:
            data = pickle.loads(self.socket.recv(MESSAGE_SIZE))
        except socket.error as e:
            print(e)
            print("No board received")
            done()
        return data

    def send(self, data):
        try:
            print("Sent: " + str(data.flag) + str(data.player), str(data.data))
            self.socket.send(pickle.dumps(data))
        except socket.error as e:
            print(e)
            print("Failed to send")

    def receive(self):
        while True:
            try:
                mess = pickle.loads(self.socket.recv(MESSAGE_SIZE))
                handle_message(mess)
            except socket.error:
                pass


net = Network()


def request_road(id):
    net.send(Message(BUILD_ROAD, my_player, id))


def request_village(id):
    net.send(Message(BUILD_VILLAGE, my_player, id))


def request_city(id):
    net.send(Message(BUILD_CITY, my_player, id))


def request_dev(id):
    pass#net.send(Message(BUILD_DEV, my_player, id))


class CircleButton:

    def __init__(self, pos, rad, func, parent):
        self.pos = pos
        self.rad = rad
        self.func = func
        self.enabled = False
        self.parent = parent

    def draw(self):
        if self.enabled:
            pygame.draw.circle(screen, YELLOW, self.pos, self.rad, 2)

    def check(self, pos):
        return dist(pos, self.pos) <= self.rad

    def press(self):
        self.func(self.parent.press_data)


class RectButton:

    def __init__(self, rect, func, parent):
        self.rect = pygame.Rect(rect)
        self.func = func
        self.enabled = False
        self.parent = parent

    def draw(self):
        if self.enabled:
            pygame.draw.rect(screen, YELLOW, self.rect, 2)

    def check(self, pos):
        return (self.rect[0] <= pos[0] <= self.rect[0] + self.rect[2]
                and self.rect[1] <= pos[1] <= self.rect[1] + self.rect[3])

    def press(self):
        self.func(self.parent.press_data)


class Dice:

    def __init__(self):
        self.val1 = 1
        self.val2 = 1
        self.x = 944
        self.y = 608
        self.rect1 = (self.x, self.y, self.x + 40, self.y + 40)
        self.rect2 = (self.x + 40, self.y, self.x + 80, self.y + 40)
        self.button = RectButton((self.x, self.y, 80, 40), beep, self)
        self.sprite = []
        for i in range(0, 7):
            self.sprite.append("")
        for i in range(1, 7):
            self.sprite[i] = pygame.image.load(data("dice" + str(i) + ".png"))

    def update(self, a, b):
        self.val1 = a
        self.val2 = b

    def draw(self):
        screen.blit(self.sprite[self.val1], self.rect1)
        screen.blit(self.sprite[self.val2], self.rect2)
        self.button.draw()

    @property
    def press_data(self):
        pass


dice = Dice()


class Resource:
    def __init__(self, color, name):
        self.color = color
        self.name = name


res = [Resource(WHITE, "Desert"), Resource(DARK_GREEN, "Wood"), Resource(ORANGE, "Clay"), Resource(YELLOW, "Wheat"),
       Resource(LIME, "Sheep"), Resource(GREY, "Stone")]


my_player = 0
current_player = 0


class Player:
    def __init__(self, color, number):
        self.color = color
        self.number = number
        self.resources = [0, 0, 0, 0, 0, 0]
        self.devs = [0, 0, 0, 0, 0]
        self.points = 0

    def add_res(self, new):
        for i in range(6):
            self.resources[i] += new[i]

    def add_devs(self, new):
        for i in range(5):
            self.devs[i] += new[i]


players = [Player(BLUE, 0), Player(WHITE, 1), Player(RED, 2), Player(YELLOW, 3)]


def clear_buttons():
    for b in enabled_buttons:
        b.enabled = False
    enabled_buttons.clear()


class Edge:

    def __init__(self, id, start, end):
        self.id = id
        self.owner = None
        self.start = start
        self.end = end
        self.full = False
        self.button = CircleButton((int((start[0] + end[0]) / 2), int((start[1] + end[1]) / 2)), 10, request_road, self)
        self.edges = []

    def draw(self):
        if self.owner is not None:
            pygame.draw.line(screen, BLACK, self.start, self.end, 7)
            pygame.draw.line(screen, players[self.owner].color, self.start, self.end, 5)
        else:
            pygame.draw.line(screen, BLACK, self.start, self.end, 3)

        self.button.draw()

    @property
    def press_data(self):
        return self.id


class Intersection:

    def __init__(self, id, pos):
        self.id = id
        self.owner = None
        self.pos = pos
        self.level = 0
        self.edges = []
        self.button = CircleButton(pos, 19, request_village, self)

    def draw(self):
        if self.owner is not None:
            pygame.draw.circle(screen, players[self.owner].color, self.pos, 20)
            pygame.draw.circle(screen, BLACK, self.pos, 20, 1)
            if self.level == 2:
                pygame.draw.circle(screen, BLACK, self.pos, 2)
        self.button.draw()

    @property
    def press_data(self):
        return self.id


class Tile:

    def __init__(self, id):
        self.id = id
        self.resource = 0
        self.number = None
        self.robber = False
        self.inters = []
        self.button = CircleButton((0, 0), 25, beep, self)

    def draw(self):
        pygame.draw.polygon(screen, res[self.resource].color, [x.pos for x in self.inters], 0)
        y = int((self.inters[3].pos[1] + self.inters[0].pos[1]) / 2)
        x = int((self.inters[1].pos[0] + self.inters[5].pos[0]) / 2)
        self.button.pos = (x, y)
        if res[self.resource].name != "Desert":
            text = tile_font.render(str(self.number), False, RED if self.number == 8 or self.number == 6 else BLACK)
            y = int((self.inters[3].pos[1] + self.inters[0].pos[1]) / 2)
            x = int((self.inters[1].pos[0] + self.inters[5].pos[0]) / 2)
            text_rect = text.get_rect(center=(x, y))
            pygame.draw.circle(screen, WHITE, (x, y), 25)
            pygame.draw.circle(screen, BLACK, (x, y), 26, 1)
            screen.blit(text, text_rect)
        if self.robber:
            pygame.draw.line(screen, BLACK, self.inters[1].pos, self.inters[4].pos, 2)
            pygame.draw.line(screen, BLACK, self.inters[2].pos, self.inters[5].pos, 2)
        self.button.draw()

    @property
    def press_data(self):
        return self.id


class Board:

    def __init__(self):
        dotrows = [3, 4, 4, 5, 5, 6, 6, 5, 5, 4, 4, 3]

        # Create intersections
        origin = (512, 80)
        y = origin[1]
        i = 0
        self.inters = []
        inter_id = 0
        for n in dotrows:
            x = origin[0] - B * (n - 1)
            l = [Intersection(inter_id, (x, y))]
            inter_id += 1
            for j in range(n - 1):
                x = x + B*2
                l.append(Intersection(inter_id, (x, y)))
                inter_id += 1
            self.inters.append(l)
            if i % 2 == 0:
                y += A
            else:
                y += L
            i += 1

        # Create edges
        self.edges = []
        edge_id = 0
        for i in range(11):
            l = []
            if dotrows[i] < dotrows[i + 1]:
                for j in range(dotrows[i]):
                    e = Edge(edge_id, self.inters[i][j].pos, self.inters[i + 1][j].pos)
                    edge_id += 1
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i+1][j].edges.append(e)

                    e = Edge(edge_id, self.inters[i][j].pos, self.inters[i + 1][j + 1].pos)
                    edge_id += 1
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i + 1][j + 1].edges.append(e)
            if dotrows[i] == dotrows[i + 1]:
                for j in range(dotrows[i]):
                    e = Edge(edge_id, self.inters[i][j].pos, self.inters[i + 1][j].pos)
                    edge_id += 1
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i + 1][j].edges.append(e)
            if dotrows[i] > dotrows[i + 1]:
                for j in range(dotrows[i + 1]):
                    e = Edge(edge_id, self.inters[i][j].pos, self.inters[i + 1][j].pos)
                    edge_id += 1
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i + 1][j].edges.append(e)

                    e = Edge(edge_id, self.inters[i][j+1].pos, self.inters[i + 1][j].pos)
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
        player, (robber, tiles) = v
        global my_player
        my_player = player
        for t in self.tiles:
            if t.id == robber:
                t.robber = True
            t.resource, t.number = tiles[t.id]

    def draw(self):
        for t in self.tiles:
            t.draw()
        for e in self.edges:
            e.draw()
        for i in self.inters:
            i.draw()

    def select_villages(self):
        clear_buttons()
        global enabled_buttons
        for l in self.inters:
            for i in l:
                has_road = True
                edge_free = True
                for e in i.edges:
                    if e.full:
                        edge_free = False
                    if e.owner == my_player:
                        has_road = True
                if has_road and edge_free:
                    i.button.enabled = True
                    enabled_buttons.append(i.button)

    def build_village(self, player, village):
        self.inters[village].owner = player
        self.inters[village].level += 1
        for e in self.inters[village].edges:
            e.full = True
        players[player].points += 1

    def select_init_village(self):
        clear_buttons()
        global enabled_buttons
        for i in self.inters:
            ok = True
            for e in i.edges:
                if e.full:
                    ok = False
            if ok:
                i.button.enabled = True
                enabled_buttons.append(i.button)

    def select_init_road(self, pos):
        clear_buttons()
        global enabled_buttons
        for e in self.inters[pos].edges:
            if not e.owner:
                e.button.enabled = True
                enabled_buttons.append(e.button)

    def select_cities(self):
        clear_buttons()
        global enabled_buttons
        for i in self.inters:
            if i.owner == my_player and i.level == 1:
                i.button.enabled = True
                enabled_buttons.append(i.button)

    def select_roads(self):
        clear_buttons()
        global enabled_buttons
        for e in self.edges:
            if e.owner is not None:
                ok = False
                for l in e.edges:
                    for j in l:
                        if j.owner == my_player:
                            ok = True
                if ok:
                    enabled_buttons.append(e)
                    e.button.enabled = True

    def build_road(self, player, road):
        self.edges[road].owner = player


board = Board()


class BuildRow:

    def __init__(self, x, y, name, resources, points, func):
        self.width = 160
        self.height = 30
        self.x = x
        self.y = y
        self.name = name
        self.resources = resources
        self.points = points
        self.button = RectButton((self.x + self.width - 50, self.y, 50, self.height), func, self)

    def draw(self):
        rect = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)

        name = build_font.render(self.name, False, BLACK)
        name_rect = name.get_rect(midleft=(self.x+2, self.y+int(self.height/2)))
        screen.blit(name, name_rect)

        gap = 2
        rad = 5
        x = name_rect.right
        y = name_rect.centery
        i = 0
        for n in self.resources:
            for j in range(n):
                x += gap + rad
                pygame.draw.circle(screen, res[i].color, (x, y), rad)
                x += gap + rad
            i += 1

        pygame.draw.rect(screen, WHITE, self.button.rect)
        pygame.draw.rect(screen, BLACK, self.button.rect, 1)
        build_text = build_font.render("Build", False, BLACK)
        build_rect = build_text.get_rect(center=self.button.rect.center)
        screen.blit(build_text, build_rect)

    @property
    def press_data(self):
        pass


class BuildCard:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rows = [
                BuildRow(x, y, "Road", [0, 1, 1], 0, board.select_roads),
                BuildRow(x, y+30, "Village", [0, 1, 1, 1, 1], 1, board.select_villages),
                BuildRow(x, y+60, "City", [0, 0, 0, 2, 0, 3], 1, board.select_cities),
                BuildRow(x, y+90, "Dev Card", [0, 0, 0, 1, 1, 1], 0, id)]

    def draw(self):
        for r in self.rows:
            r.draw()


bc = BuildCard(864, 648)


def enable_turn_buttons():
    clear_buttons()
    global enabled_buttons
    for r in bc.rows:
        r.button.enabled = True
        enabled_buttons.append(r.button)


def enable_roll_button():
    clear_buttons()
    global enabled_buttons
    dice.button.enabled = True
    enabled_buttons.append(dice.button)


def handle_message(mess):
    global current_player
    if mess.flag == START_TURN:
        current_player = mess.player
        if current_player == my_player:
            enable_roll_button()
        else:
            clear_buttons()
    elif mess.flag == ROLL:
        dice.update(mess.data[0], mess.data[1])
        if current_player == my_player:
            enable_turn_buttons()
    elif mess.flag == INIT_VILLAGE:
        board.select_init_village()
    elif mess.flag == INIT_ROAD:
        board.select_init_road(mess.data)
    elif mess.flag == BUILD_ROAD:
        board.build_road(mess.player, mess.data)
    elif mess.flag == BUILD_VILLAGE:
        board.build_village(mess.player, mess.data)
    elif mess.flag == PAY_RES:
        players[mess.player].add_res(mess.data)
    elif mess.flag == PAY_DEVS:
        players[mess.player].add_devs(mess.data)
    print("Got message with flag " + str(mess.flag))


# Exit the program
def done():
    pygame.quit()
    sys.exit()


def refresh_screen():
    screen.fill(BACK_COLOR)
    dice.draw()
    board.draw()
    bc.draw()
    pygame.display.update()


board.update_tiles(net.connect())
recv_thread = threading.Thread(target=net.receive, args=(), daemon=True)
recv_thread.start()

#board.select_init_village()

running = True
while running:
    dt = clock.tick(360)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            done()
        if e.type == pygame.USEREVENT:
            pass
        if e.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for b in enabled_buttons:
                if b.check(pos):
                    b.press()
                    break
    refresh_screen()
