
from desky.panel import Panel, render_attribute
from desky.font import default_font

@render_attribute("text", "")
@render_attribute("align", (0, 0.5))
@render_attribute("offset", (6, 0))
class Label(Panel):

    def __init__(self):
        super().__init__()
        self._font = default_font()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, _font):
        self._font = _font
        self.request_render()

    def setup(self, scheme, gui):
        scheme.setup_label(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_label(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_label(self, surface, clock, w, h)

def label_example(gui):

    cx, cy = 300, 300
    for x in range(-1, 2):
        for y in range(-1, 2):
            label = gui.create(Label)
            label.rect = (cx + x * 100, cy + y * 100, 90, 90)
            label.text = "Hello!"
            label.align = (0.5 + 0.5 * x, 0.5 + 0.5 * y)
            label.offset = (-x * 6, -y * 6)

def main():
    from desky.gui import example
    example(label_example)

if __name__ == "__main__":
    main()

