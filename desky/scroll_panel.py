
import pygame

from desky.panel import Panel
from desky.button import TextButton

class ScrollBarButton(TextButton):

    def setup(self, scheme, gui):
        scheme.setup_scroll_bar_button(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_scroll_bar_button(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_scroll_bar_button(self, surface, clock, w, h)

class ScrollBar(Panel):

    def __init__(self):
        super().__init__()
        self.button = None

    def setup(self, scheme, gui):
        scheme.setup_scroll_bar(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_scroll_bar(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_scroll_bar(self, surface, clock, w, h)

class ScrollPanel(Panel):

    def __init__(self):
        super().__init__()
        self.backpanel = None
        self.scrollbar = None

    @property
    def view_offset(self):
        return -self.backpanel.y

    @view_offset.setter
    def view_offset(self, view_offset):
        self.backpanel.y = -view_offset

    def mouse_press(self, event):
        if event.inside:
            if event.button == 4:
                self.backpanel.y = min(self.backpanel.y + 20, 0)
            elif event.button == 5:
                self.backpanel.y = max(self.backpanel.y - 20, -self.backpanel.height + self.height)

    def setup(self, scheme, gui):
        scheme.setup_scroll_panel(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_scroll_panel(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_scroll_panel(self, surface, clock, w, h)


def scroll_panel_example(gui):
    from desky.button import TextButton
    scrollpanel = gui.create(ScrollPanel)
    scrollpanel.rect = (50, 50, 200, 200)

    for y in range(30):
        button = gui.create(TextButton)
        button.rect = (0, y * 24, 100, 24)
        button.text = "Button #{}".format(y + 1)
        button.parent = scrollpanel

def main():
    from desky.gui import example
    example(scroll_panel_example)

if __name__ == "__main__":
    main()

