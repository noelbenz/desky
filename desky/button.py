
from enum import Enum
from desky.panel import Panel, RenderOnChange, render_attribute
from desky.label import Label

class ButtonState(Enum):
    NORMAL = 1,
    HOVER = 2,
    PRESSED = 3,
    DISABLED = 4

@render_attribute("state", ButtonState.NORMAL)
class TextButton(Label):

    def __init__(self):
        super().__init__()
        self.togglable = False
        self.on = False
        self.hover = None
        self.toggled = lambda on: None
        self.clicked = lambda: None
        self.accept_mouse_input = True

    def mouse_move(self, event):
        if event.hover != self.hover:
            self.hover = event.hover
            if self.state == ButtonState.NORMAL or self.state == ButtonState.HOVER:
                self.state = ButtonState.HOVER if event.hover else ButtonState.NORMAL

    def mouse_press(self, event):
        if event.hover:
            self.state = ButtonState.PRESSED

    def mouse_release(self, event):
        if event.hover:
            if not self.on:
                self.state = ButtonState.HOVER
        else:
            self.state = ButtonState.PRESSED if self.on else ButtonState.NORMAL

    def mouse_click(self, event):
        if event.hover:
            if self.togglable:
                self.on = not self.on
                self.toggled(self.on)
                self.state = ButtonState.PRESSED if self.on else ButtonState.HOVER
            else:
                self.clicked()
                self.state = ButtonState.HOVER

    def setup(self, scheme, gui):
        scheme.setup_text_button(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_text_button(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_text_button(self, surface, clock, w, h)

def button_example(gui):
    from desky.button import TextButton

    button = gui.create(TextButton)
    button.rect = (50, 50, 90, 24)
    button.text = "Normal button"
    button.align = (0.5, 0.5)
    button.offset = (0, 0)
    button.clicked = lambda: print("Clicked.")

    button = gui.create(TextButton)
    button.rect = (50, 50 + 24 + 8, 90, 24)
    button.togglable = True
    button.text = "Toggle button"
    button.align = (0.5, 0.5)
    button.offset = (0, 0)
    button.toggled = lambda on: print("Toggled: " + str(on))

def main():
    from desky.gui import example
    example(button_example)

if __name__ == "__main__":
    main()

