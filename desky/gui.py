
import pygame
import pygame.freetype
import pygame.scrap

from desky.clock import Clock
from desky.panel import Panel
from desky.layout.docking import DockLayout
from desky.scheme import Scheme, DebugScheme, DefaultScheme

class GuiEvent:
    def __init__(self):
        self.gui = None

class MouseEvent(GuiEvent):
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0
        self.button = 0
        self.inside = False
        self.hover = False

    def __str__(self):
        return (type(self).__name__ +
                "(x={}, y={}, button={}, inside={}, hover={})".format(
                    self.x, self.y, self.button, self.inside, self.hover))

class MouseMoveEvent(MouseEvent):
    def __init__(self):
        super().__init__()
        self.delta_x = 0
        self.delta_y = 0

class MousePressEvent(MouseEvent):
    pass

class MouseReleaseEvent(MouseEvent):
    pass

class MouseClickEvent(MouseEvent):
    pass

class KeyPressEvent:
    def __init__(self):
        super().__init__()
        self.hover = False
        self.focus = False
        self.uni = 0
        self.key = 0
        self.mod = 0

    def __str__(self):
        return (type(self).__name__ +
                "(hover={}, focus={}, uni={}, key={}, mod={})".format(
                    self.hover, self.focus, self.uni, self.key, self.mod))

class KeyReleaseEvent:
    def __init__(self):
        super().__init__()
        self.hover = False
        self.focus = False
        self.key = 0
        self.mod = 0

    def __str__(self):
        return (type(self).__name__ +
                "(hover={}, focus={}, key={}, mod={})".format(
                    self.hover, self.focus, self.key, self.mod))

class Gui:

    def __init__(self):
        self.world = Panel()
        self.world.accept_mouse_input = True
        self.hover = self.world
        self.focus = None
        self.press_panel = dict()
        self.scheme = Scheme()

    def create(self, cls, *args, **kwargs):
        instance = cls(*args, **kwargs)
        instance._parent = self.world
        self.world.add_child_queue.append(instance)
        instance.request_layout()
        instance.setup(self.scheme, self)
        return instance

    def find_hover(self, x, y):
        # Determine which panel the mouse is hovering over using depth-first
        # search. Higher index children have priority. Children have priority
        # over parent.
        self.hover = None
        def hover_dfs(panel, x, y):
            if panel.accept_mouse_input:
                self.hover = panel
            for child in panel.children:
                if (child.rect.contains_point(x, y)
                    and hover_dfs(child, x - child.x, y - child.y)):
                        return True
            return panel.accept_mouse_input
        # These should always succeed because the world panel is clickable by
        # default.
        assert hover_dfs(self.world, x, y), "Hover depth-first search returned false"
        assert self.hover != None, "Hover search did not find any panels."

    def broadcast_mouse_event(self, event, event_name):
        def broadcast(panel, event):
            orig_x = event.x
            orig_y = event.y
            for child in panel.children:
                event.x = orig_x - child.x
                event.y = orig_y - child.y
                broadcast(child, event)
            event.x = orig_x
            event.y = orig_y
            event.inside = (event.x >= 0 and event.y >= 0
                            and event.x < panel.width and event.y < panel.height)
            event.hover = (panel == self.hover)
            getattr(panel, event_name)(event)
        broadcast(self.world, event)

    def broadcast_key_event(self, event, event_name):
        def broadcast(panel, event):
            for child in panel.children:
                broadcast(child, event)
            event.hover = (panel == self.hover)
            event.focus = (panel == self.focus)
            getattr(panel, event_name)(event)
        broadcast(self.world, event)

    def set_focus(self, panel):
        if self.focus is not None:
            self.focus.focus_change(False)
        self.focus = panel
        panel.focus_change(True)

    def event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Determine new hover panel.
            self.find_hover(*event.pos)

            # Dispatch a mouse move event.
            gui_event = MouseMoveEvent()
            gui_event.gui = self
            gui_event.x = event.pos[0]
            gui_event.y = event.pos[1]
            gui_event.delta_x = event.rel[0]
            gui_event.delta_y = event.rel[1]
            self.broadcast_mouse_event(gui_event, "mouse_move")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Determine new hover panel.
            self.find_hover(*event.pos)
            # Remember that this hover panel has been pressed.
            self.press_panel[event.button] = self.hover

            # Make hover panel the new focus.
            self.hover.move_to_front()
            self.set_focus(self.hover)

            # Dispatch a mouse press event.
            gui_event = MousePressEvent()
            gui_event.gui = self
            gui_event.x = event.pos[0]
            gui_event.y = event.pos[1]
            gui_event.button = event.button
            self.broadcast_mouse_event(gui_event, "mouse_press")
        elif event.type == pygame.MOUSEBUTTONUP:
            # Determine new hover panel.
            self.find_hover(*event.pos)

            # Dispatch a mouse release event.
            gui_event = MouseReleaseEvent()
            gui_event.gui = self
            gui_event.x = event.pos[0]
            gui_event.y = event.pos[1]
            gui_event.button = event.button
            self.broadcast_mouse_event(gui_event, "mouse_release")

            # Get the hover panel that received the last press event.
            press_panel = self.press_panel.get(event.button, None)
            self.press_panel[event.button] = None
            # Determine if the panel was clicked on.
            if press_panel == self.hover:
                # Dispatch a mouse click event.
                gui_event = MouseClickEvent()
                gui_event.gui = self
                gui_event.x = event.pos[0]
                gui_event.y = event.pos[1]
                gui_event.button = event.button
                self.broadcast_mouse_event(gui_event, "mouse_click")
        elif event.type == pygame.KEYDOWN:
            # Dispatch a key press event.
            gui_event = KeyPressEvent()
            gui_event.gui = self
            gui_event.uni = event.unicode
            gui_event.key = event.key
            gui_event.mod = event.mod
            self.broadcast_key_event(gui_event, "key_press")
        elif event.type == pygame.KEYUP:
            # Dispatch a key release event.
            gui_event = KeyReleaseEvent()
            gui_event.gui = self
            gui_event.key = event.key
            gui_event.mod = event.mod
            self.broadcast_key_event(gui_event, "key_release")

    def layout(self, window_width, window_height):
        def remove_children(pnl):
            children = list()
            for child in pnl.children:
                if not child.marked_for_deletion:
                    remove_children(child)
                    children.append(child)
            pnl.children = children
        remove_children(self.world)

        def process_child_operations(pnl):
            # Add a new children.
            if len(pnl.add_child_queue) > 0:
                pnl.request_layout()
                for child in pnl.add_child_queue:
                    # Remove child from old parent
                    # This condition only fails for new panels. See gui.create().
                    if child in child._parent.children:
                        child._parent.children.remove(child)
                        child._parent.request_layout()
                    # Add child to new parent.
                    assert pnl is not None, "Attempted to set parent to None."
                    assert pnl is not child, "Attempted to make panel its own parent."
                    child._parent = pnl
                    pnl.children.insert(0, child)
                    child.request_layout()
            pnl.add_child_queue = []
            # Recurse over a copy of the children.
            for child in pnl.children[:]:
                # Remove child.
                if child.marked_for_deletion:
                    pnl.children.remove(child)
                    pnl.request_layout()
                process_child_operations(child)
        process_child_operations(self.world)

        if self.world.focus_request is not None:
            self.set_focus(self.world.focus_request)
            self.world.focus_request = None

        if self.world.layout_dirty:
            self.world.size = (window_width, window_height)
            iterations = 0
            while self.world.layout_dirty:
                self.world.layout_dirty = False
                self.world.process_move_queue()
                self.world.layout(self.scheme, self.world.width, self.world.height)
                iterations += 1
                if iterations > 100:
                    raise Exception("Maximum layout iterations reached.")

    def render(self, screen, clock):
        self.world.surface = screen
        self.world.render(self.scheme, screen, clock, self.world.width, self.world.height)

def example(setup):
    pygame.init()
    screen = pygame.display.set_mode((640, 640))
    pygame.freetype.init()
    pygame.scrap.init()
    pygame.key.set_repeat(400, 70)
    clock = Clock(pygame.time.Clock(), 20)
    gui = Gui()
    gui.scheme = DefaultScheme()

    setup(gui)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                gui.event(event)
        screen.fill((30, 30, 30))
        gui.layout(screen.get_width(), screen.get_height())
        gui.render(screen, clock)
        pygame.display.flip()
        clock.tick()

def input_example(gui):
    class InputPanel(Panel):
        def mouse_move(self, event):
            print(event)
        def mouse_press(self, event):
            print(event)
        def mouse_release(self, event):
            print(event)
        def mouse_click(self, event):
            print(event)
    panel = gui.create(InputPanel)
    panel.rect = (20, 30, 80, 90)
    panel.accept_mouse_input = True

def overlap_example(gui):
    panel = gui.create(Panel)
    panel.rect = (40, 40, 100, 100)
    panel.accept_mouse_input = True

    panel = gui.create(Panel)
    panel.rect = (80, 40, 100, 100)
    panel.accept_mouse_input = True

    panel = gui.create(Panel)
    panel.rect = (40, 80, 100, 100)
    panel.accept_mouse_input = True

    panel = gui.create(Panel)
    panel.rect = (80, 80, 100, 100)
    panel.accept_mouse_input = True

def main():
    example(overlap_example)

if __name__ == "__main__":
    main()

