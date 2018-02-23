
import pygame

from desky.button import ButtonState

class Scheme:
    pass

def add_default_methods(clsname):
    def default_setup(self, panel, gui):
        pass
    setattr(Scheme, "setup_" + clsname, default_setup)

    def default_layout(self, panel, w, h):
        panel.layout_children(self, w, h)
    setattr(Scheme, "layout_" + clsname, default_layout)

    def default_render(self, panel, surface, clock, w, h):
        panel.render_children(self, surface, clock, w, h)
    setattr(Scheme, "render_" + clsname, default_render)

add_default_methods("panel")
add_default_methods("label")
add_default_methods("text_button")
add_default_methods("checkbox")
add_default_methods("text_entry")
add_default_methods("context_menu_item")
add_default_methods("context_menu_sub_item")
add_default_methods("context_menu_panel")

