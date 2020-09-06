import pygame
import os

WIDTH = 1000
HEIGHT = 700
CAPTION = "Online Settlers"

# Initialize pygame and create window
pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(CAPTION)
pygame.font.init()
font = pygame.font.SysFont("arial", 12)

CLOCK = pygame.time.Clock()


def show_dice(a, b):
    pass

