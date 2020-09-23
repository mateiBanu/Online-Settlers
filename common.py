WIDTH = 1024
HEIGHT = 768
CAPTION = "Online Settlers"

BACK_COLOR = (145, 145, 145)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

L = 30

class Player:
    def __init__(self):
        self.color = RED


players = [Player]


class Map:

    def __init__(self):
        pass  #edges = [Edge for ]


class Edge:

    def __init__(self, start, end):
        self.owner = None
        self.start = start
        self.end = end
        self.full = False


class Intersection:

    def __init__(self, pos):
        self.owner = None
        self.pos = pos


class Tile:

    def __init__(self):
        pass
