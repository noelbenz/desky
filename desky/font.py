
import pygame.freetype

default = None

def default_font():
    global default
    if default == None:
        default = pygame.freetype.SysFont("Arial", 12)
    return default

