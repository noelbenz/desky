
import pygame
import pygame.freetype

from desky.vector import Vec2
from desky.graphics import Graphics
from desky.clock import Clock

class Desky:

    def __init__(self):
        self.running = False
        self.window_size = Vec2(400, 300) * 2

        pygame.init()
        pygame.font.init()
        pygame.freetype.init()
        self.screen = pygame.display.set_mode(self.window_size.as_tuple())
        self.graphics = Graphics(self.screen)
        self.clock = Clock(pygame.time.Clock(), 60)

    def start(self):
        self.setup()
        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.process_event(event)
            self.render()
            pygame.display.flip()
            self.clock.tick()

    def stop(self):
        self.running = False

    def process_event(self, event):
        """Process a pygame event."""
        if event.type == pygame.QUIT:
            self.stop()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.stop()
        else:
            if not self.map_editor.event(event):
                self.entity_manager.event(event)

    def render(self):
        self.screen.fill((30, 30, 30))
        self.graphics.offset = Vec2()
        self.map_editor.render(self.graphics, self.clock)

def main():
    app = Desky()
    Desky.start()

if __name__ == "__main__":
    main()

