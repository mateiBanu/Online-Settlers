import pygame
import os
import sys
import network
from common import *

# Initialize pygame and create window
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(CAPTION)
pygame.font.init()
font = pygame.font.SysFont("arial", 12)

clock = pygame.time.Clock()


def data(s):
    return "imgs/" + s


class Button:

    def __init__(self, rect):
        self.rect = rect
        self.enabled = True
        self.e_sprite = pygame.image.load(data("dice_button.png"))
        self.d_sprite = pygame.image.load(data("dice_empty.png"))
        self.load_imgs()

    def draw(self):
        if self.enabled:
            screen.blit(self.e_sprite, self.rect)
        else:
            screen.blit(self.d_sprite, self.rect)


class DiceButton(Button):

    def load_imgs(self):
        self.e_sprite = pygame.image.load(data("dice_button.png"))
        self.d_sprite = pygame.image.load(data("dice_empty.png"))

    def press(self):
        pass


class Dice:

    def __init__(self):
        self.val1 = 1
        self.val2 = 1
        self.x = 944
        self.y = 600
        self.rect1 = (self.x, self.y, self.x + 40, self.y + 40)
        self.rect2 = (self.x + 40, self.y, self.x + 80, self.y + 40)
        self.button = DiceButton((self.x, self.y, self.x + 80, self.y + 40))
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

    def __init__(self):
        pass

    def draw(self):
        pass


class BuildCard:

    def __init__(self):
        pass

    def draw(self):
        pass


class Player:
    def __init__(self):
        self.color = RED


players = [Player]


class Map:

    def draw(self):
        pass


class Edge:

    def draw(self):
        if self.owner:
            pygame.draw.line(screen, players[self.owner].color, self.start, self.end, 5)
        else:
            pygame.draw.line(screen, BLACK, self.start, self.end, 1)


class Intersection:

    def draw(self):
        if self.owner:
            pygame.draw.circle(screen, players[self.owner].color, self.pos, 20)


class Tile:

    def draw(self):
        pass


# Exit the program
def done():
    pygame.quit()
    sys.exit()


running = True
while running:
    screen.fill(BACK_COLOR)
    dt = clock.tick(360)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done()
    dice.draw()
    pygame.display.update()

