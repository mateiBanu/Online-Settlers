import pygame
import os
import sys
import math
import socket
import random
import threading

WIDTH = 1024
HEIGHT = 768
CAPTION = "Online Settlers"

BACK_COLOR = (0, 222, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
LIME = (51, 255, 51)
DARK_GREEN = (0, 102, 0)
GREY = (128, 128, 128)
WHITE = (255, 255, 255)

# Game Statuses
OFF_TURN = 0
ROLL = 1
TURN = 2
ROAD = 3
VILLAGE = 4
CITY = 5

status = 0

L = 80
A = int(L/2)
B = int(A * math.sqrt(3))

# Initialize pygame and create window
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(CAPTION)
pygame.font.init()
font = pygame.font.SysFont("arial", 30)

clock = pygame.time.Clock()


# Connect to the server
HOST = '127.0.0.1'
PORT = 64444


def data(s):
    return "imgs/" + s


def dist(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


def beep():
    print("BEEP!")


class Network:

    def __init__(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            self.socket.setblocking(False)
        except socket.error:
            print("Connection error")
            done()

    def receive(self):
        try:
            data, addr = self.socket.recvfrom(1024)
            e = pygame.event.Event(pygame.USEREVENT, {'data': data, 'addr': addr})
            pygame.event.post(e)
        except socket.error:
            pass


class CircleButton:

    def __init__(self, pos, rad, func):
        self.pos = pos
        self.rad = rad
        self.func = func
        self.enabled = True

    def draw(self):
        if self.enabled:
            pygame.draw.circle(screen, YELLOW, self.pos, self.rad, 1)

    def check(self, pos):
        return dist(pos, self.pos) <= self.rad

    def press(self):
        self.func()


class RectButton:

    def __init__(self, rect, func):
        self.rect = rect
        self.func = func
        self.enabled = True

    def draw(self):
        if self.enabled:
            pygame.draw.rect(screen, YELLOW, self.rect, 2)

    def check(self, pos):
        return (self.rect[0] <= pos[0] <= self.rect[0] + self.rect[2]
                and self.rect[1] <= pos[1] <= self.rect[1] + self.rect[3])

    def press(self):
        self.func()


class Dice:

    def __init__(self):
        self.val1 = 1
        self.val2 = 1
        self.x = 944
        self.y = 608
        self.rect1 = (self.x, self.y, self.x + 40, self.y + 40)
        self.rect2 = (self.x + 40, self.y, self.x + 80, self.y + 40)
        self.button = RectButton((self.x, self.y, 80, 40), beep)
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


dice = Dice()


class BuildRow:

    def __init__(self, name, resources, points):
        self.name = name
        self.resources = resources
        self.points = points
        #self.button = RectButton()

    def draw(self, x, y):
        rect = (x, y, 120, 30)
        pygame.draw.rect(screen, WHITE, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)


class BuildCard:

    def __init__(self):
        self.rows = [
                BuildRow("Road", [1, 1], 0),
                BuildRow("Village", [1, 1, 1, 1], 1),
                BuildRow("City", [0, 0, 2, 0, 3], 1),
                BuildRow("Dev Card", [0, 0, 1, 1, 1], 0)]

    def draw(self, x, y):
        i = 0
        for r in self.rows:
            r.draw(x, y+i)
            i += 30


class Resource:
    def __init__(self, color, name):
        self.color = color
        self.name = name


res = [Resource(WHITE, "Desert"), Resource(DARK_GREEN, "Wood"), Resource(ORANGE, "Clay"), Resource(YELLOW, "Wheat"),
       Resource(LIME, "Sheep"), Resource(GREY, "Stone")]


class Player:
    def __init__(self, color, name):
        self.color = color
        self.name = name


my_player = 0
players = [Player]


def get_tiles():
    v = []
    for i in range(19):
        v.append((res[random.randrange(0, 6)], random.randrange(2, 12)))
    return 9, v


class Edge:

    def __init__(self, start, end):
        self.owner = None
        self.start = start
        self.end = end
        self.full = False
        self.button = CircleButton((int((start[0] + end[0]) / 2), int((start[1] + end[1]) / 2)), 10, beep)

    def draw(self):
        if self.owner:
            pygame.draw.line(screen, players[self.owner].color, self.start, self.end, 5)
        else:
            pygame.draw.line(screen, BLACK, self.start, self.end, 3)

        self.button.draw()


class Intersection:

    def __init__(self, pos):
        self.owner = None
        self.pos = pos
        self.level = 0
        self.edges = []
        self.button = CircleButton(pos, 10, beep)

    def draw(self):
        #if self.owner:
        #    pygame.draw.circle(screen, players[self.owner].color, self.pos, 20)
        pygame.draw.circle(screen, RED, self.pos, 5)
        self.button.draw()


class Tile:

    def __init__(self):
        self.resource = res[0]
        self.number = None
        self.robber = False
        self.inters = []
        self.button = CircleButton((0, 0), 25, beep)

    def draw(self):
        pygame.draw.polygon(screen, self.resource.color, [x.pos for x in self.inters], 0)
        y = int((self.inters[3].pos[1] + self.inters[0].pos[1]) / 2)
        x = int((self.inters[1].pos[0] + self.inters[5].pos[0]) / 2)
        self.button.pos = (x, y)
        if self.resource.name != "Desert":
            text = font.render(str(self.number), False, RED if self.number == 8 or self.number == 6 else BLACK)
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


class Board:

    def __init__(self):
        dotrows = [3, 4, 4, 5, 5, 6, 6, 5, 5, 4, 4, 3]

        # Create intersections
        origin = (512, 80)
        y = origin[1]
        i = 0
        self.inters = []
        for n in dotrows:
            x = origin[0] - B * (n - 1)
            l = [Intersection((x, y))]
            for j in range(n - 1):
                x = x + B*2
                l.append(Intersection((x, y)))
            self.inters.append(l)
            if i % 2 == 0:
                y += A
            else:
                y += L
            i += 1

        # Create edges
        self.edges = []
        for i in range(11):
            l = []
            if dotrows[i] < dotrows[i + 1]:
                for j in range(dotrows[i]):
                    e = Edge(self.inters[i][j].pos, self.inters[i + 1][j].pos)
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i+1][j].edges.append(e)

                    e = Edge(self.inters[i][j].pos, self.inters[i + 1][j + 1].pos)
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i + 1][j + 1].edges.append(e)
            if dotrows[i] == dotrows[i + 1]:
                for j in range(dotrows[i]):
                    e = Edge(self.inters[i][j].pos, self.inters[i + 1][j].pos)
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i + 1][j].edges.append(e)
            if dotrows[i] > dotrows[i + 1]:
                for j in range(dotrows[i + 1]):
                    e = Edge(self.inters[i][j].pos, self.inters[i + 1][j].pos)
                    l.append(e)
                    self.inters[i][j].edges.append(e)
                    self.inters[i + 1][j].edges.append(e)

                    e = Edge(self.inters[i][j+1].pos, self.inters[i + 1][j].pos)
                    l.append(e)
                    self.inters[i][j+1].edges.append(e)
                    self.inters[i + 1][j].edges.append(e)
            self.edges.append(l)

        # Create tiles
        r, v = get_tiles()
        ind = 0
        self.tiles = []
        deltas = [(0, 0), (1, 1), (2, 1), (3, 1), (2, 0), (1, 0)]
        for l in range(0, 4, 2):
            for i in range(dotrows[l]):
                t = Tile()
                t.resource, t.number = v[ind]
                if ind == r:
                    t.robber = True
                ind += 1
                for a, b in deltas:
                    t.inters.append(self.inters[l+a][i+b])
                self.tiles.append(t)
        l = 4
        deltas = [(0, 0), (1, 1), (2, 1), (3, 0), (2, 0), (1, 0)]
        for i in range(dotrows[l]):
            t = Tile()
            t.resource, t.number = v[ind]
            if ind == r:
                t.robber = True
            ind += 1
            for a, b in deltas:
                t.inters.append(self.inters[l + a][i + b])
            self.tiles.append(t)
        deltas = [(0, 0), (1, 0), (2, 0), (3, -1), (2, -1), (1, -1)]
        for l in range(6, 10, 2):
            for i in range(1, dotrows[l]-1):
                t = Tile()
                t.resource, t.number = v[ind]
                if ind == r:
                    t.robber = True
                ind += 1
                for a, b in deltas:
                    t.inters.append(self.inters[l + a][i + b])
                self.tiles.append(t)

    def draw(self):

        for t in self.tiles:
            t.draw()

        for l in self.edges:
            for e in l:
                e.draw()

        for l in self.inters:
            for j in l:
                j.draw()

    def select_roads(self):
        for l in self.edges:
            for e in l:


def decode(message):
    #recv_thread.start()
    pass


# Exit the program
def done():
    pygame.quit()
    sys.exit()


#net = Network()
#recv_thread = threading.Thread(target=net.receive(), args=(), daemon=True)
#recv_thread.start()
board = Board()
bc = BuildCard()
running = True
while running:
    screen.fill(BACK_COLOR)
    dt = clock.tick(360)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            done()
        if e.type == pygame.USEREVENT:
            decode(e.data)
    dice.draw()
    board.draw()
    bc.draw(904, 648)
    pygame.display.update()

