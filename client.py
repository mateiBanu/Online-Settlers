import pygame
import os
import sys

WIDTH = 1024
HEIGHT = 768
CAPTION = "Online Settlers"

BACK_COLOR = (145, 145, 145)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Initialize pygame and create window
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(CAPTION)
pygame.font.init()
font = pygame.font.SysFont("arial", 12)

CLOCK = pygame.time.Clock()

def data(s):
    return "imgs/"+s

class Dice:

    def __init__(self):
        pass

    def update(self, a, b):
        pass

    def draw(self):
        pass
# Exit the program
def done():
    pygame.quit()
    sys.exit()


running = True
while running:
    SCREEN.fill(BACK_COLOR)
    dt = CLOCK.tick(360)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done()
    pygame.draw.rect(SCREEN, RED, (0,0, 40, 40))
    pygame.display.update()

