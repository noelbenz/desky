
import pygame
import pygame.freetype

from desky.vector import Vec2
from desky.graphics import Graphics
from desky.clock import Clock
from desky.gui import Gui
from desky.scheme.default import DefaultScheme
from desky.button import TextButton
from desky.checkbox import Checkbox
from desky.text_entry import TextEntry
from desky.scroll_panel import ScrollPanel

def setup(gui):

    x = 40
    y = 40

    button = gui.create(TextButton)
    button.rect = (x, y, 90, 24)
    button.text = "Normal button"
    button.align = (0.5, 0.5)
    button.offset = (0, 0)
    button.clicked = lambda: print("Clicked.")
    y += button.height + 8

    button = gui.create(TextButton)
    button.rect = (x, y, 90, 24)
    button.togglable = True
    button.text = "Toggle button"
    button.align = (0.5, 0.5)
    button.offset = (0, 0)
    button.toggled = lambda on: print("Toggled: " + str(on))
    y += button.height + 8

    checkbox = gui.create(Checkbox)
    checkbox.rect = (x, y, 190, 24)
    checkbox.text = "Checkbox example"
    y += checkbox.height + 8

    text_entry = gui.create(TextEntry)
    text_entry.rect = (x, y, 130, 24)
    y += text_entry.height + 8

    scroll_panel = gui.create(ScrollPanel)
    scroll_panel.rect = (x, y, 200, 200)
    y += scroll_panel.height + 8

    for y in range(20):
        button = gui.create(TextButton)
        button.parent = scroll_panel
        button.rect = (0, y * 24, 100, 24)
        button.text = "Button"

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    pygame.freetype.init()
    pygame.scrap.init()
    pygame.key.set_repeat(400, 70)
    clock = Clock(pygame.time.Clock(), 20)
    gui = Gui()
    gui.scheme = DefaultScheme()

    setup(gui)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                gui.event(event)
        screen.fill((30, 30, 30))
        gui.layout(screen.get_width(), screen.get_height())
        gui.render(screen, clock)
        pygame.display.flip()
        clock.tick()

if __name__ == "__main__":
    main()

