
import pygame

from desky.scheme.scheme import Scheme, render_text_entry_text
from desky.button import ButtonState
from desky.panel import Panel
from desky.scroll_panel import ScrollBar, ScrollBarButton

class DebugScheme(Scheme):
    def __init__(self):
        super().__init__()
        self.debug_colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (0, 255, 255),
            (255, 255, 0),
            (255, 0, 255),
            (255, 255, 255)
        ]
        self.button_border_colors = {
            ButtonState.NORMAL: (128, 128, 128),
            ButtonState.HOVER: (255, 255, 255),
            ButtonState.PRESSED: (255, 255, 128),
            ButtonState.DISABLED: (128, 255, 255),
        }

    def debug_render(self, panel, surface, clock, w, h):
        # Calculate the depth of this child in the element tree.
        parent_count = 0
        parent = panel.parent
        while parent != None:
            parent_count += 1
            parent = parent.parent
        # Determine color using child's depth.
        border_color = self.debug_colors[parent_count % len(self.debug_colors)]
        bg_color = (border_color[0] * 0.3, border_color[1] * 0.3, border_color[2] * 0.3)
        # Draw border.
        pygame.draw.rect(surface, border_color, pygame.Rect(0, 0, w, h))
        # Draw interior.
        pygame.draw.rect(surface, bg_color, pygame.Rect(2, 2, w - 4, h - 4))

    ############################################################################
    # Panel
    ############################################################################
    def render_panel_background(self, panel, surface, clock, w, h):
        self.debug_render(panel, surface, clock, w, h)

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
        pygame.draw.rect(surface, self.button_border_colors[panel.state], pygame.Rect(0, 0, w, h))
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(2, 2, w - 4, h - 4))

    def render_text_button(self, panel, surface, clock, w, h):
        self.render_text_button_background(panel, surface, clock, w, h)
        self.render_label_text(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Checkbox
    ############################################################################
    def layout_checkbox(self, panel, w, h):
        panel.offset = (panel.height, 0)
        panel.layout_children(self, w, h)

    def render_checkbox_background(self, panel, surface, clock, w, h):
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(6, 6, h - 12, h - 12))
        if panel.on:
            pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(h // 2 - 6, h // 2 - 6, 12, 12))

    def render_checkbox(self, panel, surface, clock, w, h):
        self.render_panel_background(panel, surface, clock, w, h)
        self.render_checkbox_background(panel, surface, clock, w, h)
        self.render_label_text(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Text Entry
    ############################################################################
    def render_text_entry(self, panel, surface, clock, w, h):
        self.render_panel_background(panel, surface, clock, w, h)
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
        panel.layout_children(self, w, h)

    def render_context_menu_panel(self, panel, surface, clock, w, h):
        self.render_panel_background(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Scroll Bar Button
    ############################################################################
    def render_scroll_bar_button(self, panel, surface, clock, w, h):
        self.render_text_button_background(panel, surface, clock, w, h);
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Scroll Bar
    ############################################################################
    def setup_scroll_bar(self, panel, gui):
        panel.button = gui.create(ScrollBarButton)
        panel.button.parent = panel

    def layout_scroll_bar(self, panel, w, h):
        view_offset = panel.view_offset
        view_height = max(panel.view_height, 1)
        total_height = max(panel.total_height, 1)
        panel.button.size = (w, min(max(view_height / total_height * h, w), h))
        panel.button.y = view_offset / (total_height - view_height) * (h - panel.button.height)
        panel.layout_children(self, w, h)

    def render_scroll_bar(self, panel, surface, clock, w, h):
        self.render_panel_background(panel, surface, clock, w, h);
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Scroll Panel
    ############################################################################
    def setup_scroll_panel(self, panel, gui):
        panel.scrollbar = gui.create(ScrollBar)
        panel.scrollbar.parent = panel

        def scroll(view_offset):
            panel.view_offset = view_offset
        panel.scrollbar.scroll = scroll

        panel.backpanel = gui.create(Panel)
        panel.backpanel.parent = panel
        panel.parent_panel = panel.backpanel

    def layout_scroll_panel(self, panel, w, h):
        panel.backpanel.width = w - 10

        height = 0
        for child in panel.backpanel.children:
            height = max(height, child.rect.bottom)
        panel.backpanel.height = height

        panel.scrollbar.rect = (panel.width - 10, 0, 10, panel.height)
        panel.scrollbar.update(panel.view_offset, panel.height, panel.backpanel.height)

        panel.layout_children(self, w, h)

    def render_scroll_panel(self, panel, surface, clock, w, h):
        self.render_panel_background(panel, surface, clock, w, h);
        panel.render_children(self, surface, clock, w, h)
