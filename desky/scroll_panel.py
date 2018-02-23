
import pygame

from desky.panel import Panel, layout_attribute
from desky.button import TextButton, ButtonState

class ScrollBarButton(TextButton):

    def setup(self, scheme, gui):
        scheme.setup_scroll_bar_button(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_scroll_bar_button(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_scroll_bar_button(self, surface, clock, w, h)

@layout_attribute("view_offset", 0)
@layout_attribute("view_height", 0)
@layout_attribute("total_height", 0)
class ScrollBar(Panel):

    def __init__(self):
        super().__init__()
        self.button = None
        self.scroll = None
        self.drag_offset = None
        self.accept_mouse_input = True

    def setup(self, scheme, gui):
        scheme.setup_scroll_bar(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_scroll_bar(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_scroll_bar(self, surface, clock, w, h)

    def update(self, view_offset, view_height, total_height):
        self.view_offset = view_offset
        self.view_height = view_height
        self.total_height = total_height

    def move_to(self, y):
        self.scroll(y / self.view_height * self.total_height - self.view_height / 2)

    def mouse_press(self, event):
        if event.hover and event.button == 1:
            self.move_to(event.y)
            self.button.state = ButtonState.PRESSED
            self.drag_offset = 0

    def mouse_move(self, event):
        if self.button.state == ButtonState.PRESSED and self.scroll:
            if self.drag_offset is None:
                self.drag_offset = self.button.y + self.button.height / 2 - event.y
            self.move_to(event.y + self.drag_offset)
        else:
            self.drag_offset = None

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
        self.backpanel.y = min(max(-view_offset, -self.backpanel.height + self.height), 0)

    def mouse_press(self, event):
        if event.inside:
            if event.button == 4:
                self.view_offset = self.view_offset - 20
            elif event.button == 5:
                self.view_offset = self.view_offset + 20

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

