
import pygame

from desky.scheme.scheme import Scheme, render_text_entry_text
from desky.scheme.debug import DebugScheme
from desky.button import ButtonState

class DefaultScheme(DebugScheme):
    def __init__(self):
        super().__init__()
        self.colors_button = {
            ButtonState.NORMAL: {
                "border": (110, 110, 110),
                "background": (47, 47, 47),
                "text": (227, 227, 227)
            },
            ButtonState.HOVER: {
                "border": (136, 136, 136),
                "background": (69, 69, 69),
                "text": (227, 227, 227)
            },
            ButtonState.PRESSED: {
                "border": (189, 189, 92),
                "background": (59, 59, 46),
                "text": (227, 227, 227)
            },
            ButtonState.DISABLED: {
                "border": (0, 0, 0),
                "background": (255, 255, 255),
                "text": (227, 227, 227)
            }
        }

        self.colors_checkbox = {
            ButtonState.NORMAL: {
                "border": (110, 110, 110),
                "background": (47, 47, 47),
            },
            ButtonState.HOVER: {
                "border": (110, 110, 110),
                "background": (47, 47, 47),
            },
            ButtonState.PRESSED: {
                "border": (110, 110, 110),
                "background": (47, 47, 47),
                "inner": (178, 178, 178)
            },
            ButtonState.DISABLED: {
                "border": (110, 110, 110),
                "background": (47, 47, 47),
                "inner": (178, 178, 178, 0)
            }
        }
        self.colors_text_entry = {
            "normal": {
                "border": (110, 110, 110),
                "background": (41, 41, 41),
                "text": (227, 227, 227)
            },
            "focus": {
                "border": (189, 189, 92),
                "background": (59, 59, 47),
                "text": (234, 234, 220)
            },
        }

    ############################################################################
    # Panel
    ############################################################################
    def render_panel_background(self, panel, surface, clock, w, h):
        pass

    def render_panel(self, panel, surface, clock, w, h):
        self.render_panel_background(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Label
    ############################################################################
    def render_label_text(self, panel, surface, clock, w, h, color=(255, 255, 255)):
        _, _, tw, th = panel.font.get_rect(panel.text)
        x = panel.align[0] * (w - tw) + panel.offset[0]
        y = panel.align[1] * (h - th) + panel.offset[1]
        panel.font.render_to(surface, (x, y), panel.text, color)

    def render_label(self, panel, surface, clock, w, h):
        self.render_panel_background(panel, surface, clock, w, h)
        self.render_label_text(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Text Button
    ############################################################################
    def render_text_button_background(self, panel, surface, clock, w, h):
        colors = self.colors_button[panel.state]
        pygame.draw.rect(surface, colors["border"], pygame.Rect(0, 0, w, h))
        pygame.draw.rect(surface, colors["background"], pygame.Rect(1, 1, w - 2, h - 2))

    def render_text_button_text(self, panel, surface, clock, w, h):
        self.render_label_text(panel, surface, clock, w, h, self.colors_button[panel.state]["text"])

    def render_text_button(self, panel, surface, clock, w, h):
        self.render_text_button_background(panel, surface, clock, w, h)
        self.render_text_button_text(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Checkbox
    ############################################################################
    def layout_checkbox(self, panel, w, h):
        panel.offset = (panel.height + 2, 0)

    def render_checkbox_background(self, panel, surface, clock, w, h):
        colors = self.colors_checkbox[panel.state]
        x, y, w, h = 4, 4, h - 8, h - 8
        pygame.draw.rect(surface, colors["border"], pygame.Rect(x, y, w, h))
        pygame.draw.rect(surface, colors["background"], pygame.Rect(x + 1, y + 1, w - 2, h - 2))
        if panel.on:
            pygame.draw.rect(surface, colors["inner"], pygame.Rect(x + 3, y + 3, w - 6, h - 6))

    def render_checkbox(self, panel, surface, clock, w, h):
        self.render_panel_background(panel, surface, clock, w, h)
        self.render_checkbox_background(panel, surface, clock, w, h)
        self.render_label_text(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Text Entry
    ############################################################################
    def render_text_entry_background(self, panel, surface, clock, w, h):
        colors = self.colors_text_entry["focus" if panel.focus else "normal"]
        pygame.draw.rect(surface, colors["border"], pygame.Rect(0, 0, w, h))
        pygame.draw.rect(surface, colors["background"], pygame.Rect(1, 1, w - 2, h - 2))
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(1, 1, w - 2, 2))
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(1, 1, 2, h - 2))

    def render_text_entry(self, panel, surface, clock, w, h):
        self.render_text_entry_background(panel, surface, clock, w, h)
        render_text_entry_text(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Context Menu
    ############################################################################
    def render_context_menu_item(self, panel, surface, clock, w, h):
        self.render_text_button(panel, surface, clock, w, h)

    def render_context_menu_sub_item(self, panel, surface, clock, w, h):
        self.render_text_button(panel, surface, clock, w, h)

    def layout_context_menu_panel(self, panel, w, h):
        panel.dock_layout.layout(panel)
        width, height = 10, 10
        for child in panel.children:
            if child.rect.right > width:
                width = child.rect.right
            if child.rect.bottom > height:
                height = child.rect.bottom
        panel.size = (width, height)

    def render_context_menu_panel(self, panel, surface, clock, w, h):
        self.render_panel_background(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Scroll Bar
    ############################################################################
    def render_scroll_bar_background(self, panel, surface, clock, w, h):
        pygame.draw.rect(surface, (59, 59, 59), pygame.Rect(0, 0, w, h))

    def render_scroll_bar(self, panel, surface, clock, w, h):
        self.render_scroll_bar_background(panel, surface, clock, w, h);
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Scroll Panel
    ############################################################################
    def render_scroll_panel_background(self, panel, surface, clock, w, h):
        pygame.draw.rect(surface, (41, 41, 41), pygame.Rect(0, 0, w, h))

    def render_scroll_panel(self, panel, surface, clock, w, h):
        self.render_scroll_panel_background(panel, surface, clock, w, h);
        panel.render_children(self, surface, clock, w, h)
