
import unittest

from desky.rect import Rect
from desky.panel import Panel
from enum import Enum
from functools import reduce, partial
from toolz.dicttoolz import valfilter

# | Type of sizing             | Maximum extra width allocation
# --------------------------------------------------------------
# | Fixed (200 px)             | 0px
# | Child (use child size)     | 0px
# | Percentage (30% of width)  | 1px
# | Custom (custom function)   | configurable
# | Even (equally divide)      | 1px
# | Fill (use remaining space) | any
#
# The types of sizing in the table above are ordered in evalulation priority.
# Fixed, Child, and Percentage sizings are evaluated first. Custom is then
# evaluated and is given the remaining area size as its argument. Even is
# evaluated next. Even panels will split remaining space evenly between
# themselves. Fill evaluates last and will take the remaining space.
#
# If the resulting layout exceeds the bounds of the parent, it is up to the
# parent to decide if it should resize.

def zero_func():
    return 0

class GridLayout:

    FIXED = 0
    CHILD = 1
    PERCENTAGE = 2
    CUSTOM = 3
    EVEN = 4
    FILL = 5

    def __init__(self, *, column_count = 1, row_count = 1, spacing = 0):
        self.panels = dict()
        self.column_sizings = dict()
        self.row_sizings = dict()
        self.column_count = column_count
        self.row_count = row_count
        self.spacing = spacing

    def add(self, panel, column, row, column_count=1, row_count=1):
        self.add_rect(panel, Rect(column, row, column_count, row_count))

    def add_rect(self, panel, rect):
        assert(rect.x >= 0)
        assert(rect.y >= 0)
        assert(rect.right <= self.column_count)
        assert(rect.bottom <= self.row_count)
        assert(self.area_empty(rect))
        self.panels[rect.frozen_copy()] = panel

    def remove(self, panel):
        self.panels = valfilter(lambda p: p != panel, self.panels)

    def clear(self, *, remove_panels):
        if remove_panels:
            for panel in self.panels.values():
                panel.remove()
        self.panels = dict()

    def area_empty(self, rect):
        for rect_other in self.panels.keys():
            if rect.intersects(rect_other):
                return False
        return True

    def set_fixed_column_sizing(self, column, size):
        self.column_sizings[column] = (self.FIXED, size)

    def set_fixed_row_sizing(self, row, size):
        self.row_sizings[row] = (self.FIXED, size)

    def set_child_column_sizing(self, column):
        self.column_sizings[column] = (self.CHILD,)

    def set_child_row_sizing(self, row):
        self.row_sizings[row] = (self.CHILD,)

    def set_percentage_column_sizing(self, column, percentage):
        self.column_sizings[column] = (self.PERCENTAGE, percentage)

    def set_percentage_row_sizing(self, row, percentage):
        self.row_sizings[row] = (self.PERCENTAGE, percentage)

    def set_custom_column_sizing(self, column, sizing_func, extra_func=zero_func):
        self.column_sizings[column] = (self.CUSTOM, sizing_func, extra_func)

    def set_custom_row_sizing(self, row, sizing_func, extra_func=zero_func):
        self.row_sizings[row] = (self.CUSTOM, sizing_func, extra_func)

    def set_even_column_sizing(self, column):
        self.column_sizings[column] = (self.EVEN,)

    def set_even_row_sizing(self, row):
        self.row_sizings[row] = (self.EVEN,)

    def set_fill_column_sizing(self, column):
        self.column_sizings[column] = (self.FILL,)

    def set_fill_row_sizing(self, row):
        self.row_sizings[row] = (self.FILL,)

    def widest_child_in_column(self, column):
        column_rect = Rect(column, 0, 1, self.row_count)
        rect_panel_tuples_that_intersect_column = list(
                filter(
                    lambda rect_panel_tuple: rect_panel_tuple[0].intersects(column_rect),
                    self.panels.items()))
        def calculate_width(rect_panel_tuple):
            rect, panel = rect_panel_tuple
            # In case a panel spans multiple columns, determine the height as a
            # proportional amount.
            return int((panel.rect_outer.w - (rect.w - 1) * self.spacing) / rect.w)
        return reduce(max, map(calculate_width, rect_panel_tuples_that_intersect_column), 0)

    def tallest_child_in_row(self, row):
        row_rect = Rect(0, row, self.column_count, 1)
        rect_panel_tuples_that_intersect_row = list(
                filter(
                    lambda rect_panel_tuple: rect_panel_tuple[0].intersects(row_rect),
                    self.panels.items()))
        def calculate_height(rect_panel_tuple):
            rect, panel = rect_panel_tuple
            # In case a panel spans multiple rows, determine the height as a
            # proportional amount.
            return int((panel.rect_outer.h - (rect.h - 1) * self.spacing) / rect.h)
        return reduce(max, map(calculate_height, rect_panel_tuples_that_intersect_row), 0)

    def layout(self, panel):

        area = (panel.rect_inner
                .move(-panel.x, -panel.y)
                .shrink(
                    0,
                    0,
                    (self.column_count - 1) * self.spacing,
                    (self.row_count - 1) * self.spacing)
                )

        column_sizings_by_type = dict()
        row_sizings_by_type = dict()

        # Group columns and rows by their sizing types while preserving the order.

        for column in range(self.column_count):
            sizing = self.column_sizings.get(column, (self.EVEN,))
            group = column_sizings_by_type.get(sizing[0], list())
            group.append((column, sizing))
            column_sizings_by_type[sizing[0]] = group

        for row in range(self.row_count):
            sizing = self.row_sizings.get(row, (self.EVEN,))
            group = row_sizings_by_type.get(sizing[0], list())
            group.append((row, sizing))
            row_sizings_by_type[sizing[0]] = group

        # Determine column widths and row heights.

        column_widths = [0 for _ in range(self.column_count)]
        row_heights = [0 for _ in range(self.row_count)]

        def calculate_fixed_sizes(sizings_by_type, sizes):
            for sizing_tuple in sizings_by_type.get(self.FIXED, []):
                column_or_row, sizing = sizing_tuple
                sizes[column_or_row] = sizing[1]
        calculate_fixed_sizes(column_sizings_by_type, column_widths)
        calculate_fixed_sizes(row_sizings_by_type, row_heights)

        def calculate_child_sizes(sizings_by_type, sizes, largest_func):
            for sizing_tuple in sizings_by_type.get(self.CHILD, []):
                column_or_row, _ = sizing_tuple
                sizes[column_or_row] = largest_func(column_or_row)
        calculate_child_sizes(column_sizings_by_type, column_widths, self.widest_child_in_column)
        calculate_child_sizes(row_sizings_by_type, row_heights, self.tallest_child_in_row)

        def calculate_percentage_sizes(sizings_by_type, sizes, area_size):
            for sizing_tuple in sizings_by_type.get(self.PERCENTAGE, []):
                column_or_row, sizing = sizing_tuple
                sizes[column_or_row] = int(area_size * sizing[1])
        calculate_percentage_sizes(column_sizings_by_type, column_widths, area.w)
        calculate_percentage_sizes(row_sizings_by_type, row_heights, area.h)

        def calculate_custom_sizes(sizings_by_type, sizes, area_size, remaining_size):
            for sizing_tuple in sizings_by_type.get(self.CUSTOM, []):
                column_or_row, sizing = sizing_tuple
                sizes[column_or_row] = int(sizing[1](area_size, remaining_size))
        calculate_custom_sizes(column_sizings_by_type, column_widths, area.w, area.w - sum(column_widths))
        calculate_custom_sizes(row_sizings_by_type, row_heights, area.h, area.h - sum(row_heights))

        def calculate_even_sizes(sizings_by_type, sizes, remaining_size):
            size = int(remaining_size / len(sizings_by_type.get(self.EVEN, [1])))
            for sizing_tuple in sizings_by_type.get(self.EVEN, []):
                column_or_row, _ = sizing_tuple
                sizes[column_or_row] = size
        calculate_even_sizes(
                column_sizings_by_type,
                column_widths,
                area.w - sum(column_widths))
        calculate_even_sizes(
                row_sizings_by_type,
                row_heights,
                area.h - sum(row_heights))

        fill_columns = column_sizings_by_type.get(self.FILL, [])
        if fill_columns:
            column_widths[fill_columns[0][0]] = area.w - sum(column_widths)
        fill_rows = row_sizings_by_type.get(self.FILL, [])
        if fill_rows:
            row_heights[fill_rows[0][0]] = area.h - sum(row_heights)

        # Allocate extra width and height to columns and rows.

        extra_width = max(area.w - sum(column_widths), 0)
        extra_height = max(area.h - sum(row_heights), 0)

        def allocate_extra_percentage(sizings_by_type, sizes, extra):
            for sizing_tuple in sizings_by_type.get(self.PERCENTAGE, []):
                column_or_row, _ = sizing_tuple
                amount = min(extra, 1)
                sizes[column_or_row] += amount
                extra -= amount
            return extra
        extra_width = allocate_extra_percentage(column_sizings_by_type, column_widths, extra_width)
        extra_height = allocate_extra_percentage(row_sizings_by_type, row_heights, extra_height)

        def allocate_extra_custom(sizings_by_type, sizes, extra):
            for sizing_tuple in sizings_by_type.get(self.CUSTOM, []):
                column_or_row, sizing = sizing_tuple
                amount = int(sizing[2](extra))
                sizes[column_or_row] += amount
                extra -= amount
            return extra
        extra_width = allocate_extra_custom(column_sizings_by_type, column_widths, extra_width)
        extra_height = allocate_extra_custom(row_sizings_by_type, row_heights, extra_height)

        def allocate_extra_even(sizings_by_type, sizes, extra):
            for sizing_tuple in sizings_by_type.get(self.EVEN, []):
                column_or_row, _ = sizing_tuple
                amount = min(extra, 1)
                sizes[column_or_row] += amount
                extra -= amount
            return extra
        extra_width = allocate_extra_even(column_sizings_by_type, column_widths, extra_width)
        extra_height = allocate_extra_even(row_sizings_by_type, row_heights, extra_height)

        # Save column widths and row heights for users to access.

        self.column_widths = column_widths
        self.row_heights = row_heights

        # Position child panels.

        for rect, panel in self.panels.items():
            x = area.x + sum(column_widths[:rect.x]) + rect.x * self.spacing
            y = area.y + sum(row_heights[:rect.y]) + rect.y * self.spacing
            width = sum(column_widths[rect.x:rect.right]) + (rect.w - 1) * self.spacing
            height = sum(row_heights[rect.y:rect.bottom]) + (rect.h - 1) * self.spacing
            panel.rect_outer = Panel.Rect(x, y, width, height)

class GridLayoutTest(unittest.TestCase):

    def setUp(self):
        from desky.gui import Gui
        self.gui = Gui()
        self.parent = self.gui.create(Panel)
        self.parent.size = (200, 300)
        self.parent.padding = (2, 3, 4, 5)
        self.parent.margins = (20, 30, 40, 50)

    def test_tallest_child_in_column_or_row_1(self):
        grid = GridLayout(column_count=5, row_count=5, spacing=3)
        for column in range(grid.column_count):
            grid.set_child_column_sizing(column)
        for row in range(grid.row_count):
            grid.set_child_row_sizing(row)

        self.assertEqual(0, grid.widest_child_in_column(2))
        self.assertEqual(0, grid.tallest_child_in_row(2))

    def test_tallest_child_in_column_or_row_2(self):
        def create_grid():
            grid = GridLayout(column_count=5, row_count=5, spacing=3)
            for column in range(grid.column_count):
                grid.set_child_column_sizing(column)
            for row in range(grid.row_count):
                grid.set_child_row_sizing(row)
            return grid

        with self.subTest("column"):
            grid = create_grid()
            child = self.gui.create(Panel)
            child.size = (60, 38)
            grid.add(child, 2, 1)

            self.assertEqual(60, grid.widest_child_in_column(2))

        with self.subTest("column"):
            grid = create_grid()
            child = self.gui.create(Panel)
            child.size = (38, 60)
            grid.add(child, 1, 2)

            self.assertEqual(60, grid.tallest_child_in_row(2))

    def test_tallest_child_in_column_or_row_3(self):
        def create_grid():
            grid = GridLayout(column_count=5, row_count=5, spacing=3)
            for column in range(grid.column_count):
                grid.set_child_column_sizing(column)
            for row in range(grid.row_count):
                grid.set_child_row_sizing(row)
            return grid

        with self.subTest("column"):
            grid = create_grid()
            child = self.gui.create(Panel)
            child.size = (66, 38)
            grid.add_rect(child, Rect(2, 1, 3, 2))

            self.assertEqual(20, grid.widest_child_in_column(2))
            self.assertEqual(20, grid.widest_child_in_column(3))
            self.assertEqual(20, grid.widest_child_in_column(4))

        with self.subTest("row"):
            grid = create_grid()
            child = self.gui.create(Panel)
            child.size = (38, 66)
            grid.add_rect(child, Rect(1, 2, 2, 3))

            self.assertEqual(20, grid.tallest_child_in_row(2))
            self.assertEqual(20, grid.tallest_child_in_row(3))
            self.assertEqual(20, grid.tallest_child_in_row(4))

    def test_area_empty(self):
        scenarios = [
                (Rect(2, 0, 4, 2), Rect(1, 1, 9, 9), False),
                (Rect(10, 2, 4, 4), Rect(1, 1, 9, 9), True),
                ]

        for rect_left, rect_right, empty in scenarios:
            with self.subTest(rect_left=rect_left, rect_right=rect_right, empty=empty):
                grid = GridLayout(column_count=20, row_count=20, spacing=5)
                grid.add_rect(self.gui.create(Panel), rect_left)
                self.assertEqual(empty, grid.area_empty(rect_right))

    def test_single_fixed(self):
        grid = GridLayout(spacing=5)
        grid.set_fixed_column_sizing(0, 90)
        grid.set_fixed_row_sizing(0, 120)

        child = self.gui.create(Panel)
        child.parent = self.parent
        child.padding = (10, 8, 6, 4)
        child.margins = (11, 16, 8, 2)
        child.size = (53, 81)
        grid.add(child, 0, 0)

        grid.layout(self.parent)

        self.assertEqual(Panel.Rect(13, 19, 71, 102), child.rect)

    def test_multiple_fixed_1(self):
        grid = GridLayout(column_count=2, row_count=2, spacing=5)
        grid.set_fixed_column_sizing(0, 101)
        grid.set_fixed_column_sizing(1, 58)
        grid.set_fixed_row_sizing(0, 33)
        grid.set_fixed_row_sizing(1, 93)

        def create_child(rect):
            child = self.gui.create(Panel)
            child.parent = self.parent
            child.padding = (10, 8, 6, 4)
            child.margins = (11, 16, 8, 2)
            child.size = (9999, 9999)
            grid.add_rect(child, rect)
            return child

        child_0_0 = create_child(Rect(0, 0, 1, 1))
        child_1_0 = create_child(Rect(1, 0, 1, 1))
        child_0_1 = create_child(Rect(0, 1, 1, 1))
        child_1_1 = create_child(Rect(1, 1, 1, 1))

        grid.layout(self.parent)

        self.assertEqual(Panel.Rect(  2,  3, 101, 33), child_0_0.rect_outer)
        self.assertEqual(Panel.Rect(108,  3,  58, 33), child_1_0.rect_outer)
        self.assertEqual(Panel.Rect(  2, 41, 101, 93), child_0_1.rect_outer)
        self.assertEqual(Panel.Rect(108, 41,  58, 93), child_1_1.rect_outer)

    def test_multiple_fixed_2(self):
        grid = GridLayout(column_count=2, row_count=2, spacing=5)
        grid.set_fixed_column_sizing(0, 101)
        grid.set_fixed_column_sizing(1, 0)
        grid.set_fixed_row_sizing(0, 0)
        grid.set_fixed_row_sizing(1, 93)

        def create_child(rect):
            child = self.gui.create(Panel)
            child.parent = self.parent
            child.padding = (10, 8, 6, 4)
            child.margins = (11, 16, 8, 2)
            child.size = (9999, 9999)
            grid.add_rect(child, rect)
            return child

        child_0_0 = create_child(Rect(0, 0, 1, 1))
        child_1_0 = create_child(Rect(1, 0, 1, 1))
        child_0_1 = create_child(Rect(0, 1, 1, 1))
        child_1_1 = create_child(Rect(1, 1, 1, 1))

        grid.layout(self.parent)

        self.assertEqual(Panel.Rect(  2,  3, 101, 18),  child_0_0.rect_outer)
        self.assertEqual(Panel.Rect(108,  3,  19, 18),  child_1_0.rect_outer)
        self.assertEqual(Panel.Rect(  2,  8, 101, 93), child_0_1.rect_outer)
        self.assertEqual(Panel.Rect(108,  8,  19, 93), child_1_1.rect_outer)

    def test_single_child(self):
        grid = GridLayout(spacing=5)
        grid.set_child_column_sizing(0)
        grid.set_child_row_sizing(0)

        child = self.gui.create(Panel)
        child.parent = self.parent
        child.padding = (10, 8, 6, 4)
        child.margins = (11, 16, 8, 2)
        child.size = (53, 81)
        grid.add(child, 0, 0)

        grid.layout(self.parent)

        self.assertEqual(Panel.Rect(13, 19, 53, 81), child.rect)

    def test_multiple_child_1(self):
        grid = GridLayout(column_count=2, row_count=2, spacing=5)
        grid.set_child_column_sizing(0)
        grid.set_child_column_sizing(1)
        grid.set_child_row_sizing(0)
        grid.set_child_row_sizing(1)

        def create_child(rect, size):
            child = self.gui.create(Panel)
            child.parent = self.parent
            child.padding = (10, 8, 6, 4)
            child.margins = (11, 16, 8, 2)
            child.size = size
            grid.add_rect(child, rect)
            return child

        child_0_0 = create_child(Rect(0, 0, 1, 1), (58, 39))
        child_1_0 = create_child(Rect(1, 0, 1, 1), (25, 71))
        child_0_1 = create_child(Rect(0, 1, 1, 1), (61, 62))
        child_1_1 = create_child(Rect(1, 1, 1, 1), (54, 20))

        grid.layout(self.parent)

        self.assertEqual(Panel.Rect( 2,  3, 80, 89), child_0_0.rect_outer)
        self.assertEqual(Panel.Rect(87,  3, 73, 89), child_1_0.rect_outer)
        self.assertEqual(Panel.Rect( 2, 97, 80, 80), child_0_1.rect_outer)
        self.assertEqual(Panel.Rect(87, 97, 73, 80), child_1_1.rect_outer)

    def test_multiple_child_2(self):
        grid = GridLayout(column_count=2, row_count=2, spacing=5)
        grid.set_child_column_sizing(0)
        grid.set_child_column_sizing(1)
        grid.set_child_row_sizing(0)
        grid.set_child_row_sizing(1)

        def create_child(rect, size):
            child = self.gui.create(Panel)
            child.parent = self.parent
            child.padding = (10, 8, 6, 4)
            child.margins = (11, 16, 8, 2)
            child.size = size
            grid.add_rect(child, rect)
            return child

        child_0_0 = create_child(Rect(0, 0, 1, 1), (58, 31))
        child_0_1 = create_child(Rect(0, 1, 1, 1), (61, 31))
        child_1_0 = create_child(Rect(1, 0, 1, 2), (25, 87))

        grid.layout(self.parent)

        self.assertEqual(Panel.Rect( 2,  3, 80,  50), child_0_0.rect_outer)
        self.assertEqual(Panel.Rect( 2, 58, 80,  50), child_0_1.rect_outer)
        self.assertEqual(Panel.Rect(87,  3, 44, 105), child_1_0.rect_outer)

    def test_single_percentage(self):
        grid = GridLayout(spacing=5)
        grid.set_percentage_column_sizing(0, 0.333)
        grid.set_percentage_row_sizing(0, 0.8)

        child = self.gui.create(Panel)
        child.parent = self.parent
        child.padding = (10, 8, 6, 4)
        child.margins = (11, 16, 8, 2)
        child.size = (53, 81)
        grid.add(child, 0, 0)

        grid.layout(self.parent)

        width = int(self.parent.rect_inner.w * 0.333) - 19 + 1
        height = int(self.parent.rect_inner.h * 0.8) - 18 + 1
        self.assertEqual(Panel.Rect(13, 19, width, height), child.rect)

    def test_multiple_percentage(self):
        grid = GridLayout(column_count=2, row_count=2, spacing=5)
        grid.set_percentage_column_sizing(0, 0.333)
        grid.set_percentage_column_sizing(1, 0.333)
        grid.set_percentage_row_sizing(0, 0.8139)
        grid.set_percentage_row_sizing(1, 1 - 0.8139)

        def create_child(rect):
            child = self.gui.create(Panel)
            child.parent = self.parent
            child.padding = (10, 8, 6, 4)
            child.margins = (11, 16, 8, 2)
            child.size = (9999, 9999)
            grid.add_rect(child, rect)
            return child

        child_0_0 = create_child(Rect(0, 0, 1, 1))
        child_0_1 = create_child(Rect(0, 1, 1, 1))
        child_1_0 = create_child(Rect(1, 0, 1, 1))
        child_1_1 = create_child(Rect(1, 1, 1, 1))

        grid.layout(self.parent)

        width_0 = int(189 * 0.333) + 1
        width_1 = width_0
        height_0 = int(287 * 0.8139) + 1
        height_1 = int(287 * (1 - 0.8139))
        self.assertEqual(Panel.Rect(2,           3,            width_0, height_0), child_0_0.rect_outer)
        self.assertEqual(Panel.Rect(2,           8 + height_0, width_0, height_1), child_0_1.rect_outer)
        self.assertEqual(Panel.Rect(7 + width_0, 3,            width_1, height_0), child_1_0.rect_outer)
        self.assertEqual(Panel.Rect(7 + width_0, 8 + height_0, width_1, height_1), child_1_1.rect_outer)

    def test_single_custom(self):

        def custom_sizing(area_size, remaining_size):
            return area_size ** 0.5

        def custom_extra(extra):
            return extra / 2

        grid = GridLayout(spacing=5)
        grid.set_custom_column_sizing(0, custom_sizing, custom_extra)
        grid.set_custom_row_sizing(0, custom_sizing, custom_extra)

        child = self.gui.create(Panel)
        child.parent = self.parent
        child.padding = (10, 8, 6, 4)
        child.margins = (11, 16, 8, 2)
        child.size = (53, 81)
        grid.add(child, 0, 0)

        grid.layout(self.parent)

        root_width = int(194 ** 0.5)
        root_height = int(292 ** 0.5)
        final_width = root_width + int((194 - root_width) / 2) - 19
        final_height = root_height + int((292 - root_height) / 2) - 18

        self.assertEqual(Panel.Rect(13, 19, final_width, final_height), child.rect)

    def test_multiple_custom(self):

        def custom_sizing_1(area_size, remaining_size):
            return area_size ** 0.8

        def custom_sizing_2(area_size, remaining_size):
            return area_size - area_size ** 0.8

        grid = GridLayout(column_count=2, row_count=2, spacing=5)
        grid.set_custom_column_sizing(0, custom_sizing_1, partial(min, 1))
        grid.set_custom_column_sizing(1, custom_sizing_2, partial(min, 1))
        grid.set_custom_row_sizing(0, custom_sizing_2, partial(min, 1))
        grid.set_custom_row_sizing(1, custom_sizing_1, partial(min, 1))

        def create_child(rect):
            child = self.gui.create(Panel)
            child.parent = self.parent
            child.padding = (10, 8, 6, 4)
            child.margins = (11, 16, 8, 2)
            child.size = (9999, 9999)
            grid.add_rect(child, rect)
            return child

        child_0_0 = create_child(Rect(0, 0, 1, 1))
        child_0_1 = create_child(Rect(0, 1, 1, 1))
        child_1_0 = create_child(Rect(1, 0, 1, 1))
        child_1_1 = create_child(Rect(1, 1, 1, 1))

        grid.layout(self.parent)

        width_0 = int(custom_sizing_1(189, None)) + 1
        width_1 = int(custom_sizing_2(189, None))
        height_0 = int(custom_sizing_2(287, None)) + 1
        height_1 = int(custom_sizing_1(287, None))

        self.assertEqual(Panel.Rect(2,           3,            width_0, height_0), child_0_0.rect_outer)
        self.assertEqual(Panel.Rect(2,           8 + height_0, width_0, height_1), child_0_1.rect_outer)
        self.assertEqual(Panel.Rect(7 + width_0, 3,            width_1, height_0), child_1_0.rect_outer)
        self.assertEqual(Panel.Rect(7 + width_0, 8 + height_0, width_1, height_1), child_1_1.rect_outer)

    def test_single_even(self):
        # Since even sizing is the default we should make sure it works even
        # when we don't excplicitly set the columns and rows to even sizing.
        for default in (True, False):
            with self.subTest(default=default):
                grid = GridLayout(spacing=5)
                if not default:
                    grid.set_even_column_sizing(0)
                    grid.set_even_row_sizing(0)

                child = self.gui.create(Panel)
                child.parent = self.parent
                child.padding = (10, 8, 6, 4)
                child.margins = (11, 16, 8, 2)
                child.size = (53, 81)
                grid.add(child, 0, 0)

                grid.layout(self.parent)

                self.assertEqual(Panel.Rect(13, 19, 175, 274), child.rect)

    def test_multiple_even(self):
        grid = GridLayout(column_count=2, row_count=2, spacing=5)
        grid.set_even_column_sizing(0)
        grid.set_even_column_sizing(1)
        grid.set_even_row_sizing(0)
        grid.set_even_row_sizing(1)

        def create_child(rect):
            child = self.gui.create(Panel)
            child.parent = self.parent
            child.padding = (10, 8, 6, 4)
            child.margins = (11, 16, 8, 2)
            child.size = (9999, 9999)
            grid.add_rect(child, rect)
            return child

        child_0_0 = create_child(Rect(0, 0, 1, 1))
        child_0_1 = create_child(Rect(0, 1, 1, 1))
        child_1_0 = create_child(Rect(1, 0, 1, 1))
        child_1_1 = create_child(Rect(1, 1, 1, 1))

        grid.layout(self.parent)

        width_0 = int(189 * 0.5) + 1
        width_1 = int(189 * 0.5)
        height_0 = int(287 * 0.5) + 1
        height_1 = int(287 * 0.5)

        self.assertEqual(Panel.Rect(2,           3,            width_0, height_0), child_0_0.rect_outer)
        self.assertEqual(Panel.Rect(2,           8 + height_0, width_0, height_1), child_0_1.rect_outer)
        self.assertEqual(Panel.Rect(7 + width_0, 3,            width_1, height_0), child_1_0.rect_outer)
        self.assertEqual(Panel.Rect(7 + width_0, 8 + height_0, width_1, height_1), child_1_1.rect_outer)

    def test_single_fill(self):
        grid = GridLayout(spacing=5)
        grid.set_fill_column_sizing(0)
        grid.set_fill_row_sizing(0)

        child = self.gui.create(Panel)
        child.parent = self.parent
        child.padding = (10, 8, 6, 4)
        child.margins = (11, 16, 8, 2)
        child.size = (53, 81)
        grid.add(child, 0, 0)

        grid.layout(self.parent)

        self.assertEqual(Panel.Rect(13, 19, 175, 274), child.rect)

    def test_multiple_fill(self):
        grid = GridLayout(column_count=2, row_count=2, spacing=5)
        grid.set_percentage_column_sizing(0, 0.3333)
        grid.set_fill_column_sizing(1)
        grid.set_fill_row_sizing(0)
        grid.set_fixed_row_sizing(1, 100)

        def create_child(rect):
            child = self.gui.create(Panel)
            child.parent = self.parent
            child.padding = (10, 8, 6, 4)
            child.margins = (11, 16, 8, 2)
            child.size = (9999, 9999)
            grid.add_rect(child, rect)
            return child

        child_0_0 = create_child(Rect(0, 0, 1, 1))
        child_0_1 = create_child(Rect(0, 1, 1, 1))
        child_1_0 = create_child(Rect(1, 0, 1, 1))
        child_1_1 = create_child(Rect(1, 1, 1, 1))

        grid.layout(self.parent)

        width_0 = int(189 * 0.3333)
        width_1 = 189 - int(189 * 0.3333)
        height_0 = 287 - 100
        height_1 = 100

        self.assertEqual(Panel.Rect(2,           3,            width_0, height_0), child_0_0.rect_outer)
        self.assertEqual(Panel.Rect(2,           8 + height_0, width_0, height_1), child_0_1.rect_outer)
        self.assertEqual(Panel.Rect(7 + width_0, 3,            width_1, height_0), child_1_0.rect_outer)
        self.assertEqual(Panel.Rect(7 + width_0, 8 + height_0, width_1, height_1), child_1_1.rect_outer)

def grid_example(gui):
    panel = gui.create(Panel)
    panel.rect = (50, 50, 500, 500)
    panel.padding = (8, 16, 24, 32)

    grid = GridLayout(column_count = 3, row_count = 4, spacing = 4)

    for row in range(0, grid.row_count):
        for column in range(0, grid.column_count):
            child = gui.create(Panel)
            child.parent = panel
            grid.add(child, column, row)

    grid.layout(panel)


def main():
    from desky.gui import example
    #example(grid_example)
    unittest.main()

if __name__ == "__main__":
    main()

