
import unittest

class Rect:

    def __init__(self, x, y, w, h):
        self._x = x
        self._y = y
        self._w = w
        self._h = h

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    @property
    def w(self):
        return self._w

    @w.setter
    def w(self, w):
        self._w = w

    @property
    def h(self):
        return self._h

    @h.setter
    def h(self, h):
        self._h = h

    @property
    def right(self):
        return self.x + self.w

    @property
    def bottom(self):
        return self.y + self.h

    def move(self, x, y):
        self.x += x
        self.y += y
        return self

    def shrink(self, x, y, w, h):
        self.x += x
        self.y += y
        self.w = max(self.w - x - w, 0)
        self.h = max(self.h - y - h, 0)
        return self

    def expand(self, x, y, w, h):
        self.x -= x
        self.y -= y
        self.w += x + w
        self.h += y + h
        return self

    def as_tuple(self):
        return (self.x, self.y, self.w, self.h)

    def copy(self):
        return Rect(self.x, self.y, self.w, self.h)

    def contains_point(self, x, y):
        return (x >= self.x and y >= self.y
                and x < self.x + self.w and y < self.y + self.h)

    def __eq__(self, other):
        if isinstance(other, Rect):
            return (self.x == other.x and self.y == other.y
                    and self.w == other.w and self.h == other.h)
        return False

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Rect({}, {}, {}, {})".format(self.x, self.y, self.w, self.h)

class RectTest(unittest.TestCase):

    def new_rect(self, *args, **kwargs):
        return Rect(*args, **kwargs)

    def test_x(self):
        rect = self.new_rect(1, 2, 3, 4)
        self.assertEqual(1, rect.x)
        rect.x = 9
        self.assertEqual(9, rect.x)

    def test_y(self):
        rect = self.new_rect(1, 2, 3, 4)
        self.assertEqual(2, rect.y)
        rect.y = 9
        self.assertEqual(9, rect.y)

    def test_w(self):
        rect = self.new_rect(1, 2, 3, 4)
        self.assertEqual(3, rect.w)
        rect.w = 9
        self.assertEqual(9, rect.w)

    def test_h(self):
        rect = self.new_rect(1, 2, 3, 4)
        self.assertEqual(4, rect.h)
        rect.h = 9
        self.assertEqual(9, rect.h)

    def test_right(self):
        rect = self.new_rect(3, 10, 9, 20)
        self.assertEqual(12, rect.right)

    def test_bottom(self):
        rect = self.new_rect(3, 10, 9, 20)
        self.assertEqual(30, rect.bottom)

    def test_eq(self):
        rect1 = self.new_rect(1, 2, 3, 4)
        rect2 = self.new_rect(1, 2, 3, 4)
        rect3 = self.new_rect(2, 2, 3, 4)
        self.assertTrue(rect1 == rect1)
        self.assertTrue(rect2 == rect2)
        self.assertTrue(rect3 == rect3)
        self.assertTrue(rect1 == rect2)
        self.assertTrue(rect1 != rect3)
        self.assertTrue(rect2 != rect3)

    def test_move(self):
        rect = self.new_rect(1, 2, 3, 4)
        rect.move(5, 8)
        self.assertEqual(self.new_rect(6, 10, 3, 4), rect)

    def test_shrink(self):
        rect = self.new_rect(10, 10, 10, 10)
        rect.shrink(1, 2, 3, 4)
        self.assertEqual(self.new_rect(11, 12, 6, 4), rect)

    def test_expand(self):
        rect = self.new_rect(10, 10, 10, 10)
        rect.expand(1, 2, 3, 4)
        self.assertEqual(self.new_rect(9, 8, 14, 16), rect)

    def test_copy(self):
        rect = self.new_rect(1, 2, 3, 4)
        rect_copy = rect.copy()
        self.assertEqual(rect, rect_copy)
        self.assertFalse(rect is rect_copy)

