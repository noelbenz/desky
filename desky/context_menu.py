
from desky.panel import Panel, render_attribute
from desky.button import TextButton
from desky.layout.docking import DockLayout

class ContextMenuItem(TextButton):
    """A context menu button."""

    def __init__(self):
        super().__init__()
        self.clicked = lambda: None
        self.root_menu = None

    def mouse_move(self, event):
        # Remove submenu peers when we hover over this item.
        if event.hover:
            self.parent.remove_submenus()
        super().mouse_move(event)

    def mouse_press(self, event):
        # Run the callback and remove the entire menu system.
        if event.hover:
            self.clicked()
            self.root_menu.hide()

    def setup(self, scheme, gui):
        scheme.setup_context_menu_item(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_context_menu_item(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_context_menu_item(self, surface, clock, w, h)

class ContextMenuSubItem(TextButton):
    """A context menu item that reveals a submenu when hovered over."""

    def __init__(self):
        super().__init__()
        self.submenu = None

    def mouse_move(self, event):
        # Remove submenu peers then show this submenu when we hover over this
        # panel.
        if event.hover and self.submenu.is_hidden:
            self.parent.remove_submenus()
            self.submenu.show(event.gui, self.absolute_x + self.width, self.absolute_y)
        super().mouse_move(event)

    def show(self, gui, x, y):
        self.submenu.show(gui, x, y)

    def hide(self):
        self.submenu.hide()

    def setup(self, scheme, gui):
        scheme.setup_context_menu_sub_item(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_context_menu_sub_item(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_context_menu_sub_item(self, surface, clock, w, h)

class ContextMenuPanel(Panel):
    """A container for context menu items."""

    def __init__(self):
        super().__init__()
        self.subitems = []
        self.dock_layout = DockLayout()
        # Set when this is a submenu
        self.root_menu = None

    def add(self, item):
        item.parent = self
        self.dock_layout.dock_top(item)
        # Remember submenu items.
        if isinstance(item, ContextMenuSubItem):
            self.subitems.append(item)

    def inside(self, world_x, world_y):
        """
        Determine if the world coordinates given is within this menu or within
        a submenu.
        """
        x, y = self.to_local((world_x, world_y))
        # Point is inside this panel
        if x >= 0 and y >= 0 and x < x + self.width and y < y + self.height:
            return True
        # Check if the point is inside a submenu.
        else:
            for subitem in self.subitems:
                if subitem.submenu.inside(world_x, world_y):
                    return True
        # Point is outside the entire menu tree.
        return False

    def remove_submenus(self):
        for subitem in self.subitems:
            subitem.submenu.hide()

    def remove(self):
        """
        Remove this menu and all its submenus.
        """
        # Remove this menu and all submenus.
        self.remove_submenus()
        super().remove()

    def mouse_press(self, event):
        # When a mouse press occurs outside a menu system we want to close the
        # entire menu system.

        # Let the root_menu handle click checks.
        if self.root_menu is not None:
            return
        else:
            # Mouse point is outside this menu and all submenus.
            if not self.inside(event.x, event.y):
                self.remove()

    def setup(self, scheme, gui):
        scheme.setup_context_menu_panel(self, gui)

    def layout(self, scheme, w, h):
        scheme.layout_context_menu_panel(self, w, h)

    def render(self, scheme, surface, clock, w, h):
        scheme.render_context_menu_panel(self, surface, clock, w, h)


class ContextMenu:

    def __init__(self):
        super().__init__()
        self.items = []
        self.menu = None
        self.root_menu = self
        self.width = 120

    def item(self, text, callback=None):
        self.items.append((1, text, callback))

    def submenu(self, text):
        menu = ContextMenu()
        menu.root_menu = self.root_menu
        self.items.append((2, text, menu))
        return menu

    def show(self, gui, x, y):
        self.hide()
        self.menu = gui.create(ContextMenuPanel)
        self.menu.pos = (x, y)
        self.menu.width = self.width
        self.menu.root_menu = self.root_menu
        for item_type, text, extra in self.items:
            # item, extra is callback
            if item_type == 1:
                item_pnl = gui.create(ContextMenuItem)
                item_pnl.height = 20
                item_pnl.text = text
                item_pnl.root_menu = self.root_menu
                if extra is not None:
                    item_pnl.clicked = extra
                self.menu.add(item_pnl)
            # submenu, extra is ContextMenu
            elif item_type == 2:
                item_pnl = gui.create(ContextMenuSubItem)
                item_pnl.height = 20
                item_pnl.text = text
                item_pnl.submenu = extra
                self.menu.add(item_pnl)
            # separator
            elif item_type == 3:
                pass
            # error
            else:
                raise Exception("Unexpected item type {} in context menu.".format(item_type))

    def hide(self):
        if self.menu is not None:
            self.menu.remove()
            self.menu = None

    @property
    def is_hidden(self):
        return self.menu is None

    def inside(self, x, y):
        return not self.is_hidden and self.menu.inside(x, y)

def context_menu_example(gui):
    menu = ContextMenu()

    for i in range(1, 5):
        name = "Item #" + str(i)
        menu.item(name, lambda name=name: print(name))

    submenu = menu.submenu("Submenu #1")
    for i in range(1, 5):
        name = "Submenu Item #" + str(i)
        submenu.item(name, lambda name=name: print(name))

    submenu = menu.submenu("Submenu #2")
    for i in range(1, 5):
        name = "Submenu Item #" + str(i)
        submenu.item(name, lambda name=name: print(name))

    subsubmenu = submenu.submenu("Subsubmenu #1")
    for i in range(1, 5):
        name = "Subsubmenu Item #" + str(i)
        subsubmenu.item(name, lambda name=name: print(name))

    class BackPanel(Panel):
        def __init__(self):
            super().__init__()
            self.accept_mouse_input = True

        def mouse_click(self, event):
            if event.hover and event.button == 3:
                menu.show(event.gui, event.x, event.y)

        def layout(self, scheme, w, h):
            self.rect = self.parent.rect

    gui.create(BackPanel)
    menu.show(gui, 50, 50)

def main():
    from desky.gui import example
    example(context_menu_example)

if __name__ == "__main__":
    main()

