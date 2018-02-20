
import re
import pygame

from desky.clock import Clock
from desky.panel import Panel, render_attribute
from desky.font import default_font

ignore_keys = [
    pygame.K_LSHIFT,
    pygame.K_RSHIFT,
    pygame.K_LCTRL,
    pygame.K_RCTRL,
    pygame.K_LALT,
    pygame.K_RALT,
    pygame.K_LMETA,
    pygame.K_RMETA,
    pygame.K_LSUPER,
    pygame.K_RSUPER,
    pygame.K_NUMLOCK,
    pygame.K_CAPSLOCK,
    pygame.K_SCROLLOCK,
    pygame.K_MODE,
    pygame.K_HELP,
    pygame.K_PRINT,
    pygame.K_SYSREQ,
    pygame.K_BREAK,
    pygame.K_MENU,
    pygame.K_POWER,
    pygame.K_EURO,
    pygame.K_PAGEUP,
    pygame.K_PAGEDOWN,
    pygame.K_PAUSE,
    pygame.K_CLEAR,
    pygame.K_F1,
    pygame.K_F2,
    pygame.K_F3,
    pygame.K_F4,
    pygame.K_F5,
    pygame.K_F6,
    pygame.K_F7,
    pygame.K_F8,
    pygame.K_F9,
    pygame.K_F10,
    pygame.K_F11,
    pygame.K_F12,
    pygame.K_F13,
    pygame.K_F14,
    pygame.K_F15
]

@render_attribute("text", "")
@render_attribute("caret", 0)
@render_attribute("select_start", 0)
@render_attribute("viewx", 0)
@render_attribute("xoffset", 6)
class TextEntry(Panel):

    def __init__(self):
        super().__init__()
        self.accept_mouse_input = True
        self._font = default_font()
        self.focus = False
        self.selecting = False
        self.time_last_click = 0

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, _font):
        self._font = _font
        self.request_render()

    def cursor_to_caret(self, cursor_x, cursor_y=0):
        absolute_mx = cursor_x + self.viewx
        caret = 0
        distance = absolute_mx
        while caret <= len(self.text):
            _, _, tw, _ = self.font.get_rect(self.text[:caret])
            if tw >= absolute_mx:
                if distance < abs(absolute_mx - tw):
                    # The caret in the previous position was closer to cursor.
                    caret = max(caret - 1, 0)
                break
            if caret == len(self.text):
                break
            distance = abs(absolute_mx - tw)
            caret += 1
        return caret

    def mouse_press(self, event):
        double_click_speed = 0.4
        time = Clock.time()
        if event.hover and len(self.text) > 0:
            # Single click
            if time > self.time_last_click + double_click_speed:
                self.caret = self.cursor_to_caret(event.x, event.y)
                self.select_start = self.caret
                self.selecting = True
            #Double click
            else:
                caret = self.cursor_to_caret(event.x, event.y)
                start, end = sorted((self.caret, self.select_start))
                # Currently no selection.
                if start == end:
                    # Click was on caret.
                    if caret == start:
                        # Special case when caret is at the end of the text.
                        if start == len(self.text):
                            start -= 1
                        match_after = re.search(r"^\w+", self.text[start:])
                        match_before = None
                        # We're selecting a word.
                        if match_after:
                            match_before = re.search(r"\w*$", self.text[:start])
                        # We're selecting non-word characters.
                        else:
                            match_after = re.search(r"^[^\w]+", self.text[start:])
                            match_before = re.search(r"[^\w]*$", self.text[:start])
                        # Select matched characters.
                        self.select_start = match_before.span()[0]
                        self.caret = match_before.span()[1] + match_after.span()[1]

                # There is a selection.
                else:
                    # Click was inside selection.
                    if caret >= start and caret <= end:
                        self.select_start = 0
                        self.caret = len(self.text)
            self.time_last_click = time

    def mouse_move(self, event):
        if self.selecting:
            self.caret = self.cursor_to_caret(event.x, event.y)

    def mouse_release(self, event):
        self.selecting = False

    def focus_change(self, focus):
        self.focus = focus
        self.request_render()

    def key_press(self, event):
        if event.focus:
            ctrl = event.mod & (pygame.KMOD_LCTRL | pygame.KMOD_RCTRL)
            shift = event.mod & (pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT)

            if event.key == pygame.K_BACKSPACE:
                if self.select_start == self.caret and self.caret > 0:
                    self.text = self.text[:self.caret - 1] + self.text[self.caret:]
                    self.caret -= 1
                    self.select_start -= 1
                else:
                    start, end = sorted((self.caret, self.select_start))
                    self.text = self.text[:start] + self.text[end:]
                    self.caret = start
                    self.select_start = self.caret
            elif event.key == pygame.K_LEFT:
                if ctrl:
                    start = self.caret
                    if not shift:
                        start, _ = sorted((self.caret, self.select_start))
                    match = re.search(r"\w+[^\w]*$", self.text[:start])
                    if match is None:
                        self.caret = 0
                    else:
                        self.caret = match.span()[0]
                    if not shift:
                        self.select_start = self.caret
                elif shift:
                    if self.caret > 0:
                        self.caret -= 1
                else:
                    start, end = sorted((self.caret, self.select_start))
                    if start == end:
                        if start > 0:
                            self.caret -= 1
                            self.select_start = self.caret
                    else:
                        self.caret = start
                        self.select_start = self.caret
            elif event.key == pygame.K_RIGHT:
                if ctrl:
                    end = self.caret
                    if not shift:
                        _, end = sorted((self.caret, self.select_start))
                    match = re.search(r"[^\w]*\w+", self.text[end:])
                    if match is None:
                        self.caret = len(self.text)
                    else:
                        self.caret = end + match.span()[1]
                    if not shift:
                        self.select_start = self.caret
                elif shift:
                    if self.caret < len(self.text):
                        self.caret += 1
                else:
                    start, end = sorted((self.caret, self.select_start))
                    if start == end:
                        if start < len(self.text):
                            self.caret += 1
                            self.select_start = self.caret
                    else:
                        self.caret = end
                        self.select_start = self.caret
            elif event.key == pygame.K_HOME:
                self.caret = 0
                if not shift:
                    self.select_start = self.caret
            elif event.key == pygame.K_END:
                self.caret = len(self.text)
                if not shift:
                    self.select_start = self.caret
            elif event.key == pygame.K_DELETE:
                start, end = sorted((self.caret, self.select_start))
                if start == end:
                    self.text = self.text[:self.caret] + self.text[self.caret + 1:]
                else:
                    self.text = self.text[:start] + self.text[end:]
                    self.caret = start
                    self.select_start = self.caret
            elif event.key in ignore_keys:
                pass
            else:
                if ctrl:
                    if event.key == pygame.K_v:
                        start, end = sorted((self.caret, self.select_start))
                        clipboard = pygame.scrap.get("text/plain;charset=utf-8")
                        if clipboard is not None:
                            # print(','.join('{:02X}'.format(x) for x in clipboard))
                            clipboard = clipboard[:-2].decode("utf-16le")
                            self.text = self.text[:start] + clipboard + self.text[end:]
                            self.caret = start + len(clipboard)
                            self.select_start = self.caret
                    if event.key == pygame.K_c or event.key == pygame.K_x:
                        start, end = sorted((self.caret, self.select_start))
                        if start != end:
                            text = self.text[start:end]
                            data = text.encode("utf-16le") + bytes("\x00\x00", "ascii")
                            pygame.scrap.put("text/plain;charset=utf-8", data)
                        if event.key == pygame.K_x:
                            self.text = self.text[:start] + self.text[end:]
                            self.caret = start
                            self.select_start = self.caret
                    if event.key == pygame.K_a:
                        self.select_start = 0
                        self.caret = len(self.text)
                else:
                    start, end = sorted((self.caret, self.select_start))
                    self.text = self.text[:start] + event.uni + self.text[end:]
                    self.caret = start + 1
                    self.select_start = self.caret

    def setup(self, scheme, gui):
        scheme.setup_text_entry(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_text_entry(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_text_entry(self, surface, clock, w, h)

def text_entry_example(gui):

    text_entry = gui.create(TextEntry)
    text_entry.rect = (50, 50, 190, 30)
    text_entry.request_focus()

def main():
    from desky.gui import example
    example(text_entry_example)

if __name__ == "__main__":
    main()

