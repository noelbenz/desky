
from desky.panel import Panel, layout_attribute
from desky.button import TextButton
from desky.layout.grid import GridLayout

class AdjustableDividerGrabber(TextButton):

    def __init__(self):
        super().__init__()
        self.grab_point = None
        self.adjust = lambda dx, dy, final: None

    def setup(self, scheme, gui):
        scheme.setup_adjustable_divider_grabber(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_adjustable_divider_grabber(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_adjustable_divider_grabber(self, surface, clock, w, h)

    def mouse_press(self, event):
        super().mouse_press(event)
        if event.hover:
            self.grab_point = self.to_world((event.x, event.y))

    def mouse_release(self, event):
        super().mouse_release(event)
        if self.grab_point:
            global_pos = self.to_world((event.x, event.y))
            self.adjust(global_pos[0] - self.grab_point[0], global_pos[1] - self.grab_point[1], True)
            self.grab_point = None

    def mouse_move(self, event):
        super().mouse_move(event)
        if self.grab_point:
            global_pos = self.to_world((event.x, event.y))
            self.adjust(global_pos[0] - self.grab_point[0], global_pos[1] - self.grab_point[1], False)

@layout_attribute("divider_size", 8)
class AdjustableDivider(Panel):

    def __init__(self, *, column_count=1, row_count=1, divider_size=8):
        super().__init__()
        self.grid = GridLayout(
                column_count=column_count * 2 - 1,
                row_count=row_count * 2 - 1)
        self.saved_column_widths = None
        self.saved_row_heights = None
        self.divider_size = divider_size
        self.grabbers = list()

    @property
    def column_count(self):
        return (self.grid.column_count + 1) // 2

    @column_count.setter
    def column_count(self, column_count):
        self.grid.column_count = column_count * 2 - 1
        self.request_layout()

    @property
    def row_count(self):
        return (self.grid.row_count + 1) // 2

    @row_count.setter
    def row_count(self, row_count):
        self.grid.row_count = row_count * 2 - 1
        self.request_layout()

    def add(self, panel, *, column=0, row=0):
        panel.parent = self
        self.grid.add(panel, column * 2, row * 2)

    def set_column_size(self, column, size):
        self.grid.set_fixed_column_sizing(column * 2, size)

    def set_row_size(self, row, size):
        self.grid.set_fixed_row_sizing(row * 2, size)

    def fix_columns_and_rows(self):
        for column in range(self.column_count - 1):
            self.grid.set_fixed_column_sizing(
                    column * 2, self.saved_column_widths[column * 2])
        for row in range(self.row_count - 1):
            self.grid.set_fixed_row_sizing(
                    row * 2, self.saved_row_heights[row * 2])

        # Always use fill for the last row and column.
        self.grid.set_fill_column_sizing(self.grid.column_count - 1)
        self.grid.set_fill_row_sizing(self.grid.row_count - 1)

    def update_grabbers(self, gui):
        grabber_count = len(self.grabbers)
        new_grabber_count = ((self.column_count - 1) * self.row_count +
                            self.column_count * (self.row_count - 1) +
                            (self.column_count - 1) * (self.row_count - 1))

        # Create new grabbers
        if new_grabber_count > grabber_count:
            for _ in range(new_grabber_count - grabber_count):
                self.grabbers.append(gui.create(AdjustableDividerGrabber))
        # Or remove extra grabbers
        elif new_grabber_count < grabber_count:
            for grabber in range(self.grabbers[0:grabber_count - new_grabber_count]):
                grabber.remove()
            self.grabbers = self.grabbers[grabber_count - new_grabber_count:]

        # Add grabbers to grid
        self.grid.clear(remove_panels=False)
        it = iter(self.grabbers)

        # Place column grabbers
        for column in range(self.column_count - 1):
            for row in range(self.row_count):
                grabber = next(it)
                grabber.parent = self
                grabber.adjust = lambda dx, dy, final, column=column, row=row: self.adjust(column, row, dx, None, final)
                self.grid.add(grabber, column * 2 + 1, row * 2)

        # Place row grabbers
        for row in range(self.row_count - 1):
            for column in range(self.column_count):
                grabber = next(it)
                grabber.parent = self
                grabber.adjust = lambda dx, dy, final, column=column, row=row: self.adjust(column, row, None, dy, final)
                self.grid.add(grabber, column * 2, row * 2 + 1)

        # Place intersection grabbers
        for column in range(self.column_count - 1):
            for row in range(self.row_count - 1):
                grabber = next(it)
                grabber.parent = self
                grabber.adjust = lambda dx, dy, final, column=column, row=row: self.adjust(column, row, dx, dy, final)
                self.grid.add(grabber, column * 2 + 1, row * 2 + 1)

        # Size grabber rows to divider_size
        for column in range(self.column_count - 1):
            self.grid.set_fixed_column_sizing(column * 2 + 1, self.divider_size)
        for row in range(self.row_count - 1):
            self.grid.set_fixed_row_sizing(row * 2 + 1, self.divider_size)


    def adjust(self, column, row, dx, dy, final):
        # Save column widths and row heights when we begin dragging.
        if not self.saved_column_widths:
            self.saved_column_widths = self.grid.column_widths
            self.saved_row_heights = self.grid.row_heights
            self.fix_columns_and_rows()

        # Adjust the column and row sizes.
        if dx:
            self.grid.set_fixed_column_sizing(
                    column * 2,
                    max(self.saved_column_widths[column * 2] + dx, 0))
        if dy:
            self.grid.set_fixed_row_sizing(
                    row * 2,
                    max(self.saved_row_heights[row * 2] + dy, 0))

        # When we finish dragging, destroy the saved column widths and row heights.
        if final:
            self.saved_column_widths = None
            self.saved_row_heights = None

        self.request_layout()

    def setup(self, scheme, gui):
        scheme.setup_adjustable_divider(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_adjustable_divider(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_adjustable_divider(self, surface, clock, w, h)

def adjustable_divider_example(gui):

    divider = gui.create(AdjustableDivider, column_count=3, row_count=4)
    divider.rect = (50, 50, 400, 400)

    for column in range(3):
        for row in range(4):
            child = gui.create(Panel)
            divider.add(child, column=column, row=row)

def main():
    from desky.gui import example
    example(adjustable_divider_example)

if __name__ == "__main__":
    main()

