
import unittest

import pygame

from desky.rect import Rect, RectTest

class LayoutOnChange:
    def __init__(self, private_name, default):
        self.private_name = private_name
        self.default = default

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name, self.default)

    def __set__(self, obj, default):
        if self.__get__(obj) != default:
            setattr(obj, self.private_name, default)
            obj.request_layout()

class RenderOnChange:
    def __init__(self, private_name, default):
        self.private_name = private_name
        self.default = default

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name, self.default)

    def __set__(self, obj, default):
        if self.__get__(obj) != default:
            setattr(obj, self.private_name, default)
            obj.request_render()

def add_layout_attribute(cls, name, default):
    private_name = "_" + name
    setattr(cls, private_name, default)
    setattr(cls, name, LayoutOnChange(private_name, default))

def add_render_attribute(cls, name, default):
    private_name = "_" + name
    setattr(cls, private_name, default)
    setattr(cls, name, RenderOnChange(private_name, default))

def layout_attribute(name, default):
    def dec(cls):
        add_layout_attribute(cls, name, default)
        return cls
    return dec

def render_attribute(name, default):
    def dec(cls):
        add_render_attribute(cls, name, default)
        return cls
    return dec

class Panel:

    class Rect(Rect):
        """
        Panel.Rect extends Rect to add layout requests on change. This makes it
        safe to update individual properties or call non-const methods of a
        Panel's rect, margin, or padding, i.e. panel.margin.x = 6 or
        panel.rect.shrink(3, 2, 3, 4).
        """

        def __init__(self, x, y, w, h, panel = None):
            super().__init__(x, y, w, h)
            self.panel = panel

        @Rect.x.setter
        def x(self, x):
            if self._x == x:
                return
            self._x = x
            if self.panel:
                self.panel.request_layout()

        @Rect.y.setter
        def y(self, y):
            if self._y == y:
                return
            self._y = y
            if self.panel:
                self.panel.request_layout()

        @Rect.w.setter
        def w(self, w):
            if self._w == w:
                return
            self._w = w
            if self.panel:
                self.panel.request_layout()

        @Rect.h.setter
        def h(self, h):
            if self._h == h:
                return
            self._h = h
            if self.panel:
                self.panel.request_layout()

        def copy(self):
            return Panel.Rect(self.x, self.y, self.w, self.h)

    def __init__(self):
        self._parent = None
        self.children = list()
        self._rect = Panel.Rect(0, 0, 0, 0, self)
        self._margins = Panel.Rect(0, 0, 0, 0, self)
        self._padding = Panel.Rect(0, 0, 0, 0, self)
        self.setup_dirty = True
        self.layout_dirty = True
        self.render_dirty = True
        self.surface = None
        self.accept_mouse_input = False
        self.focus_request = None
        self.parent_panel = None
        # Children-modifying operations are not safe to perform during events,
        # layout, render, etc. since those events iterate over the children.
        self.move_queue = []
        self.add_child_queue = []
        self.marked_for_deletion = False

    def move_to_front(self):
        if self._parent is None:
            return
        self._parent.move_queue.append((self, 0))
        self.parent.request_layout()

    def move_to_back(self):
        if self._parent is None:
            return
        self._parent.move_queue.append((self, -1))
        self.parent.request_layout()

    def process_move_queue(self):
        if len(self.move_queue) == 0:
            return

        for child, index in self.move_queue:
            # Child was removed after move was queued.
            if not child in self.children:
                return
            self.children.remove(child)
            if index < 0:
                index = len(self.children) + index + 1
            self.children.insert(index, child)

        self.move_queue = []

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, rect):
        if isinstance(rect, tuple):
            rect = Panel.Rect(*rect, self)

        self.x = rect.x
        self.y = rect.y
        self.width = rect.w
        self.height = rect.h

    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, padding):
        if isinstance(padding, tuple):
            padding = Panel.Rect(*padding, self)

        if self._padding == padding:
            return
        self._padding = padding
        self._padding.panel = self
        self.request_layout()

    @property
    def margins(self):
        return self._margins

    @margins.setter
    def margins(self, margins):
        if isinstance(margins, tuple):
            margins = Panel.Rect(*margins, self)

        if self._margins == margins:
            return
        self._margins = margins
        self._margins.panel = self
        self.request_layout()

    @property
    def rect_inner(self):
        return self.rect.copy().shrink(*self.padding.as_tuple())

    @rect_inner.setter
    def rect_inner(self, rect):
        self.rect = rect.copy().expand(*self.padding.as_tuple())
        self._rect.panel = self

    @property
    def rect_outer(self):
        return self.rect.copy().expand(*self.margins.as_tuple())

    @rect_outer.setter
    def rect_outer(self, rect):
        self.rect = rect.copy().shrink(*self.margins.as_tuple())
        self._rect.panel = self

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, x):
        self.rect.x = x

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, y):
        self.rect.y = y

    @property
    def width(self):
        return self.rect.w

    @width.setter
    def width(self, width):
        self.rect.w = width

    @property
    def height(self):
        return self.rect.h

    @height.setter
    def height(self, height):
        self.rect.h = height

    @property
    def pos(self):
        return (self.x, self.y)

    @pos.setter
    def pos(self, pos):
        self.x = pos[0]
        self.y = pos[1]

    @property
    def size(self):
        return (self.width, self.height)

    @size.setter
    def size(self, size):
        self.width = size[0]
        self.height = size[1]

    @property
    def absolute_x(self):
        if self.parent is None:
            return self.x
        else:
            return self.x + self.parent.absolute_x

    @property
    def absolute_y(self):
        if self.parent is None:
            return self.y
        else:
            return self.y + self.parent.absolute_y

    def to_world(self, pos):
        if self.parent is None:
            return pos
        else:
            return self.parent.to_world((self.x + pos[0], self.y + pos[1]))

    def to_local(self, pos):
        if self.parent is None:
            return pos
        else:
            local_to_parent = self.parent.to_local(pos)
            return (local_to_parent[0] - self.x, local_to_parent[1] - self.y)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        assert(parent is not None)
        assert(parent is not self)
        assert(self._parent is not None)
        if self._parent is parent:
            return
        while parent.parent_panel is not None:
            parent = parent.parent_panel
        parent.add_child_queue.append(self)
        parent.request_layout()

    def request_setup(self):
        if not self.layout_dirty:
            self.request_layout()
        if self.setup_dirty:
            return
        self.setup_dirty = True

    def request_layout(self):
        if not self.render_dirty:
            self.request_render()
        if self.layout_dirty:
            return
        self.layout_dirty = True
        if self.parent:
            self.parent.request_layout()

    def request_render(self):
        if self.render_dirty:
            return
        self.render_dirty = True
        if self.parent:
            self.parent.request_render()

    def request_focus(self, panel=None):
        if panel is None:
            panel = self
        if self.parent is None:
            self.focus_request = panel
        else:
            self.parent.request_focus(panel)

    def remove(self):
        if self.marked_for_deletion:
            return
        self.marked_for_deletion = True
        self.request_layout()

    @property
    def removed(self):
        return self.marked_for_deletion

    def mouse_move(self, event):
        pass

    def mouse_press(self, event):
        pass

    def mouse_release(self, event):
        pass

    def mouse_click(self, event):
        pass

    def key_press(self, event):
        pass

    def key_release(self, event):
        pass

    def focus_change(self, focus):
        pass

    def setup(self, scheme, gui):
        scheme.setup_panel(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_panel(self, w, h)

    def layout_children(self, scheme, w, h):
        for child in self.children:
            iterations = 0
            while child.layout_dirty:
                child.layout_dirty = False
                child.process_move_queue()
                child.layout(scheme, child.width, child.height)
                iterations += 1
                if iterations > 100:
                    raise Exception("Maximum layout iterations reached.")

    def render(self, scheme, surface, clock, w, h):
        scheme.render_panel(self, surface, clock, w, h)

    def render_children(self, scheme, surface, clock, w, h):
        # The last drawn child will on top and the first child in the list
        # is the top panel, so we render in reverse order.
        for child in reversed(self.children):
            # Create a new surface if needed.
            if child.surface == None or child.surface.get_size() != child.size:
                child.surface = pygame.Surface(child.size, pygame.SRCALPHA)
                child.render_dirty = True

            if child.render_dirty:
                child.surface.fill((0, 0, 0, 0))
                # Render the child.
                child.render(
                        scheme,
                        child.surface,
                        clock,
                        child.width,
                        child.height)

            # Render child surface to parent surface.
            self.surface.blit(child.surface, (child.x, child.y))

        self.render_dirty = False

class PanelRectTest(RectTest):
    def new_rect(self, *args, **kwargs):
        return Panel.Rect(*args, **kwargs, panel=None)

class PanelTest(unittest.TestCase):

    def setUp(self):
        from gui.gui import Gui
        self.gui = Gui()
        self.panel = self.gui.create(Panel)
        self.panel.rect = Rect(50, 80, 100, 120)
        self.panel.padding = Rect(2, 3, 5, 11)
        self.panel.margins = Rect(17, 23, 29, 37)
        self.panel.layout_dirty = False
        self.gui.world.layout_dirty = False

    def test_rect(self):
        self.assertEqual(Rect(50, 80, 100, 120), self.panel.rect)

        rect = Rect(11, 22, 33, 44)
        self.panel.rect = rect.as_tuple()
        self.assertEqual(rect, self.panel.rect)
        self.assertTrue(self.panel.layout_dirty)

        self.panel.layout_dirty = False
        self.panel.rect = rect
        self.assertFalse(self.panel.layout_dirty)
        self.panel.rect = rect.as_tuple()
        self.assertFalse(self.panel.layout_dirty)

    def test_padding(self):
        self.assertEqual(Rect(2, 3, 5, 11), self.panel.padding)

        rect = Rect(11, 22, 33, 44)
        self.panel.padding = rect.as_tuple()
        self.assertEqual(rect, self.panel.padding)
        self.assertTrue(self.panel.layout_dirty)

        self.panel.layout_dirty = False
        self.panel.padding = rect
        self.assertFalse(self.panel.layout_dirty)

    def test_margins(self):
        self.assertEqual(Rect(17, 23, 29, 37), self.panel.margins)

        rect = Rect(11, 22, 33, 44)
        self.panel.margins = rect.as_tuple()
        self.assertEqual(rect, self.panel.margins)
        self.assertTrue(self.panel.layout_dirty)

        self.panel.layout_dirty = False
        self.panel.margins = rect
        self.assertFalse(self.panel.layout_dirty)

    def test_inner(self):
        self.assertEqual(Rect(52, 83, 93, 106), self.panel.rect_inner)

        rect = Rect(22, 33, 44, 55)
        self.panel.rect_inner = rect
        self.assertEqual(rect, self.panel.rect_inner)
        self.assertEqual(Rect(20, 30, 51, 69), self.panel.rect)
        self.assertTrue(self.panel.layout_dirty)

        self.panel.layout_dirty = False
        self.panel.rect_inner = rect
        self.assertFalse(self.panel.layout_dirty)

    def test_outer(self):
        self.assertEqual(Rect(33, 57, 146, 180), self.panel.rect_outer)

        rect = Rect(55, 66, 77, 88)
        self.panel.rect_outer = rect
        self.assertEqual(rect, self.panel.rect_outer)
        self.assertEqual(Rect(72, 89, 31, 28), self.panel.rect)
        self.assertTrue(self.panel.layout_dirty)

        self.panel.layout_dirty = False
        self.panel.rect_outer = rect
        self.assertFalse(self.panel.layout_dirty)

    def test_x(self):
        self.assertEqual(50, self.panel.x)
        self.panel.x = 127
        self.assertEqual(Rect(127, 80, 100, 120), self.panel.rect)
        self.assertTrue(self.panel.layout_dirty)

        self.panel.layout_dirty = False
        self.panel.x = 127
        self.assertFalse(self.panel.layout_dirty)

    def test_y(self):
        self.assertEqual(80, self.panel.y)
        self.panel.y = 127
        self.assertEqual(Rect(50, 127, 100, 120), self.panel.rect)
        self.assertTrue(self.panel.layout_dirty)

        self.panel.layout_dirty = False
        self.panel.y = 127
        self.assertFalse(self.panel.layout_dirty)

    def test_width(self):
        self.assertEqual(100, self.panel.width)
        self.panel.width = 127
        self.assertEqual(Rect(50, 80, 127, 120), self.panel.rect)
        self.assertTrue(self.panel.layout_dirty)

        self.panel.layout_dirty = False
        self.panel.width = 127
        self.assertFalse(self.panel.layout_dirty)

    def test_height(self):
        self.assertEqual(120, self.panel.height)
        self.panel.height = 127
        self.assertEqual(Rect(50, 80, 100, 127), self.panel.rect)
        self.assertTrue(self.panel.layout_dirty)

        self.panel.layout_dirty = False
        self.panel.height = 127
        self.assertFalse(self.panel.layout_dirty)

    def test_pos(self):
        self.assertEqual((50, 80), self.panel.pos)
        self.panel.pos = (127, 99)
        self.assertEqual(Rect(127, 99, 100, 120), self.panel.rect)
        self.assertTrue(self.panel.layout_dirty)

        self.panel.layout_dirty = False
        self.panel.pos = (127, 99)
        self.assertFalse(self.panel.layout_dirty)

    def test_size(self):
        self.assertEqual((100, 120), self.panel.size)
        self.panel.size = (127, 99)
        self.assertEqual(Rect(50, 80, 127, 99), self.panel.rect)
        self.assertTrue(self.panel.layout_dirty)

        self.panel.layout_dirty = False
        self.panel.size = (127, 99)
        self.assertFalse(self.panel.layout_dirty)

    def test_parent(self):
        self.assertIs(self.gui.world, self.panel.parent)
        self.panel.parent = self.gui.world
        self.assertFalse(self.panel.layout_dirty)

        parent = self.gui.create(Panel)
        self.assertTrue(self.gui.world.layout_dirty)
        self.gui.world.layout_dirty = False

        self.panel.parent = parent
        self.assertNotIn(self.panel, self.gui.world.children)
        self.assertIn(self.panel, parent.children)
        self.assertTrue(self.panel.layout_dirty)
        self.assertTrue(parent.layout_dirty)
        self.assertTrue(self.gui.world.layout_dirty)

    def test_request_layout(self):
        self.assertFalse(self.panel.layout_dirty)
        self.assertFalse(self.gui.world.layout_dirty)
        self.panel.request_layout()
        self.assertTrue(self.panel.layout_dirty)
        self.assertTrue(self.gui.world.layout_dirty)

if __name__ == "__main__":
    unittest.main()

