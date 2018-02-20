
import pygame

from desky.vector import Vec2

class Graphics:
    """Host of methods for rendering basic primitives."""

    def __init__(self, screen):
        self.screen = screen
        self.offset = Vec2()

    def rect(self, x, y, w, h, color):
        """Draws a rectangle."""
        x += self.offset.x
        y += self.offset.y
        self.screen.fill(color.as_tuple(), pygame.Rect(int(x), int(y), int(w), int(h)))

    def blit(self, surface, x, y):
        """Render a surface onto the screen."""
        self.screen.blit(surface, (x + self.offset.x, y + self.offset.y))

