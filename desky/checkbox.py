
from desky.panel import Panel, render_attribute
from desky.button import TextButton

class Checkbox(TextButton):

    def __init__(self):
        super().__init__()
        self.togglable = True

    def setup(self, scheme, gui):
        scheme.setup_checkbox(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_checkbox(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_checkbox(self, surface, clock, w, h)

def checkbox_example(gui):

    checkbox = gui.create(Checkbox)
    checkbox.rect = (50, 50, 190, 30)
    checkbox.text = "Checkbox example"

def main():
    from desky.gui import example
    example(checkbox_example)

if __name__ == "__main__":
    main()

