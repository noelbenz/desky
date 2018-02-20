
import unittest

from desky.panel import Panel

class DockLayout:

    TOP = 0
    BOTTOM = 1
    LEFT = 2
    RIGHT = 3
    FILL = 4

    def __init__(self):
        self.panels = list()

    def dock_top(self, panel):
        self.panels.append((panel, self.TOP))

    def dock_bottom(self, panel):
        self.panels.append((panel, self.BOTTOM))

    def dock_left(self, panel):
        self.panels.append((panel, self.LEFT))

    def dock_right(self, panel):
        self.panels.append((panel, self.RIGHT))

    def dock_fill(self, panel):
        self.panels.append((panel, self.FILL))

    def layout(self, panel):
        area = panel.rect_inner.move(-panel.x, -panel.y)
        for item in self.panels:
            child = item[0]
            side = item[1]

            if side == self.TOP:
                outer_h = child.rect_outer.h
                child.rect_outer = Panel.Rect(area.x, area.y, area.w, outer_h)
                area.shrink(0, outer_h, 0, 0)
            elif side == self.BOTTOM:
                outer_h = child.rect_outer.h
                child.rect_outer = Panel.Rect(area.x, area.bottom - outer_h, area.w, outer_h)
                area.shrink(0, 0, 0, outer_h)
            elif side == self.LEFT:
                outer_w = child.rect_outer.w
                child.rect_outer = Panel.Rect(area.x, area.y, outer_w, area.h)
                area.shrink(outer_w, 0, 0, 0)
            elif side == self.RIGHT:
                outer_w = child.rect_outer.w
                child.rect_outer = Panel.Rect(area.right - outer_w, area.y, outer_w, area.h)
                area.shrink(0, 0, outer_w, 0)
            elif side == self.FILL:
                child.rect_outer = Panel.Rect(area.x, area.y, area.w, area.h)

class DockLayoutTest(unittest.TestCase):

    def setUp(self):
        from desky.gui import Gui
        self.gui = Gui()
        self.parent = self.gui.create(Panel)
        self.parent.size = (200, 300)
        self.parent.padding = (2, 3, 4, 5)
        self.parent.margins = (20, 30, 40, 50)
        self.child_top = self.gui.create(Panel)
        self.child_bottom = self.gui.create(Panel)
        self.child_left = self.gui.create(Panel)
        self.child_right = self.gui.create(Panel)
        self.child_fill = self.gui.create(Panel)
        for child in (self.child_top, self.child_bottom, self.child_left,
                      self.child_right, self.child_fill):
            child.padding = (10, 8, 6, 4)
            child.margins = (11, 16, 8, 2)
        self.layout = DockLayout()

    def test_top(self):
        self.child_top.parent = self.parent
        self.child_top.size = (33, 44)
        self.layout.dock_top(self.child_top)
        self.layout.layout(self.parent)
        self.assertEqual(Panel.Rect(13, 19, 175, 44), self.child_top.rect)
        self.gui.layout(1000, 1000)
        self.assertFalse(self.child_top.layout_dirty)
        self.layout.layout(self.parent)
        self.assertFalse(self.child_top.layout_dirty)
        self.assertFalse(self.parent.layout_dirty)
        self.assertFalse(self.gui.world.layout_dirty)

    def test_bottom(self):
        self.child_bottom.parent = self.parent
        self.child_bottom.size = (33, 44)
        self.layout.dock_bottom(self.child_bottom)
        self.layout.layout(self.parent)
        self.assertEqual(Panel.Rect(13, 249, 175, 44), self.child_bottom.rect)
        self.gui.layout(1000, 1000)
        self.assertFalse(self.child_bottom.layout_dirty)
        self.layout.layout(self.parent)
        self.assertFalse(self.child_bottom.layout_dirty)
        self.assertFalse(self.parent.layout_dirty)
        self.assertFalse(self.gui.world.layout_dirty)

    def test_left(self):
        self.child_left.parent = self.parent
        self.child_left.size = (33, 44)
        self.layout.dock_left(self.child_left)
        self.layout.layout(self.parent)
        self.assertEqual(Panel.Rect(13, 19, 33, 274), self.child_left.rect)
        self.gui.layout(1000, 1000)
        self.assertFalse(self.child_left.layout_dirty)
        self.layout.layout(self.parent)
        self.assertFalse(self.child_left.layout_dirty)
        self.assertFalse(self.parent.layout_dirty)
        self.assertFalse(self.gui.world.layout_dirty)

    def test_right(self):
        self.child_right.parent = self.parent
        self.child_right.size = (33, 44)
        self.layout.dock_right(self.child_right)
        self.layout.layout(self.parent)
        self.assertEqual(Panel.Rect(155, 19, 33, 274), self.child_right.rect)
        self.gui.layout(1000, 1000)
        self.assertFalse(self.child_right.layout_dirty)
        self.layout.layout(self.parent)
        self.assertFalse(self.child_right.layout_dirty)
        self.assertFalse(self.parent.layout_dirty)
        self.assertFalse(self.gui.world.layout_dirty)

    def test_fill(self):
        self.child_fill.parent = self.parent
        self.child_fill.size = (33, 44)
        self.layout.dock_fill(self.child_fill)
        self.layout.layout(self.parent)
        self.assertEqual(Panel.Rect(13, 19, 175, 274), self.child_fill.rect)
        self.gui.layout(1000, 1000)
        self.assertFalse(self.child_fill.layout_dirty)
        self.layout.layout(self.parent)
        self.assertFalse(self.child_fill.layout_dirty)
        self.assertFalse(self.parent.layout_dirty)
        self.assertFalse(self.gui.world.layout_dirty)

def dock_example(gui):
    panel = gui.create(Panel)
    panel.rect = (50, 50, 500, 500)
    panel.padding = (8, 16, 24, 32)

    layout = DockLayout()

    child_top = gui.create(Panel)
    child_top.parent = panel
    child_top.height = 80
    child_top.margins = (32, 24, 16, 8)
    layout.dock_top(child_top)

    child_right = gui.create(Panel)
    child_right.parent = panel
    child_right.width = 80
    child_right.margins = (32, 24, 16, 8)
    layout.dock_right(child_right)

    child_bottom = gui.create(Panel)
    child_bottom.parent = panel
    child_bottom.height = 80
    child_bottom.margins = (32, 24, 16, 8)
    layout.dock_bottom(child_bottom)

    child_left = gui.create(Panel)
    child_left.parent = panel
    child_left.width = 80
    child_left.margins = (32, 24, 16, 8)
    layout.dock_left(child_left)

    child_fill = gui.create(Panel)
    child_fill.parent = panel
    child_fill.margins = (32, 24, 16, 8)
    layout.dock_fill(child_fill)

    layout.layout(panel)


def main():
    from desky.gui import example
    unittest.main()
    example(dock_example)

if __name__ == "__main__":
    main()

