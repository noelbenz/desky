
import pygame

class Clock:
    """Simple wrapper around pygame's clock."""

    def __init__(self, pygame_clock, desired_fps):
        self.pygame_clock = pygame_clock
        self.desired_fps = desired_fps

    @property
    def delta(self):
        """Return time elapsed since the previous frame."""
        return self.pygame_clock.get_time() / 1000

    @staticmethod
    def time():
        """Returns elapsed time since pygame.init() in seconds."""
        return pygame.time.get_ticks() / 1000

    @property
    def fps(self):
        """Return the approximate framerate."""
        return self.pygame_clock.get_fps()

    def tick(self):
        """Called once per frame and causes the process to wait to achieve the
        desired framerate."""
        self.pygame_clock.tick(self.desired_fps)


