
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
add_default_methods("scroll_panel")
add_default_methods("scroll_bar")
add_default_methods("scroll_bar_button")

def render_text_entry_text(panel, surface, clock, w, h):
    # Get measurements.
    ascender = panel.font.get_sized_ascender()
    descender = panel.font.get_sized_descender()
    th = panel.font.get_sized_height()
    _, _, startx, _ = panel.font.get_rect(panel.text[:panel.caret])
    basex, basey, _, _ = panel.font.get_rect(panel.text)

    # Update the view.
    if panel.caret == 0:
        panel.viewx = -panel.xoffset
    else:
        if startx - panel.viewx > panel.width:
            panel.viewx = startx - int(panel.width * 0.66)
        if startx - panel.viewx < 0:
            panel.viewx = startx - int(panel.width * 0.33)
        panel.viewx = max(panel.viewx, -panel.xoffset)

    # Draw main text portion.
    x = -panel.viewx
    y = int(0.5 * (h - th))
    tx = x
    ty = y - basey + descender + th
    textsurf, _ = panel.font.render(None, (255, 255, 255))
    surface.blit(textsurf, (tx, ty))

    if panel.focus:
        # Determine caret / highlight start coordinates.
        start, end = sorted((panel.caret, panel.select_start))
        _, _, startx, _ = panel.font.get_rect(panel.text[:start])
        # Default endx and color so we get a white caret with a 1px width.
        endx = startx + 1
        color = (255, 255, 255)
        # Determine highlight end coordinate and adjust endx and color.
        if start != end:
            _, _, endx, _ = panel.font.get_rect(panel.text[:end])
            color = (128, 128, 255)
        # Draw the caret or selection area.
        pygame.draw.rect(surface, color, pygame.Rect(tx + startx, 0.5 * (h - th), endx - startx, th))
        if start != end:
            # Draw selection text. To get the selected text correctly
            # positioned we align the last pixel of the selected text with
            # endx.
            basex, basey, tw, _ = panel.font.get_rect(panel.text[start:end])
            ty = y -basey + descender + th
            textsurf, _ = panel.font.render(None, (0, 0, 127))
            surface.blit(textsurf, (tx + endx - tw, ty))

