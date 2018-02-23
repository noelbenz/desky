
import pygame

from desky.scheme.scheme import Scheme
from desky.button import ButtonState

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
    def _render_panel(self, panel, surface, clock, w, h):
        self.debug_render(panel, surface, clock, w, h)

    def render_panel(self, panel, surface, clock, w, h):
        self._render_panel(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Label
    ############################################################################
    def _render_label(self, panel, surface, clock, w, h, color=(255, 255, 255)):
        _, _, tw, th = panel.font.get_rect(panel.text)
        x = panel.align[0] * (w - tw) + panel.offset[0]
        y = panel.align[1] * (h - th) + panel.offset[1]
        panel.font.render_to(surface, (x, y), panel.text, color)

    def render_label(self, panel, surface, clock, w, h):
        self._render_panel(panel, surface, clock, w, h)
        self._render_label(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Text Button
    ############################################################################
    def _render_text_button(self, panel, surface, clock, w, h):
        pygame.draw.rect(surface, self.button_border_colors[panel.state], pygame.Rect(0, 0, w, h))
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(2, 2, w - 4, h - 4))

    def render_text_button(self, panel, surface, clock, w, h):
        self._render_text_button(panel, surface, clock, w, h)
        self._render_label(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Checkbox
    ############################################################################
    def layout_checkbox(self, panel, w, h):
        panel.offset = (panel.height, 0)

    def _render_checkbox(self, panel, surface, clock, w, h):
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(6, 6, h - 12, h - 12))
        if panel.on:
            pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(h // 2 - 6, h // 2 - 6, 12, 12))

    def render_checkbox(self, panel, surface, clock, w, h):
        self._render_panel(panel, surface, clock, w, h)
        self._render_checkbox(panel, surface, clock, w, h)
        self._render_label(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)

    ############################################################################
    # Text Entry
    ############################################################################
    def _render_text_entry(self, panel, surface, clock, w, h):
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

    def render_text_entry(self, panel, surface, clock, w, h):
        self._render_panel(panel, surface, clock, w, h)
        self._render_text_entry(panel, surface, clock, w, h)
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
        self._render_panel(panel, surface, clock, w, h)
        panel.render_children(self, surface, clock, w, h)


