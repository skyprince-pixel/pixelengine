"""PixelEngine Declarative Layouts and Grouping.

This module provides structural classes that make building UIs and complex
scenes vastly easier, especially for AI agents that struggle with math constraints.
"""

from pixelengine.pobject import PObject

class Group(PObject):
    """A logical grouping of multiple PObjects.
    
    When a Group is moved (via self.x or self.y), rotated, or its opacity altered,
    it automatically applies the transformation to its children.
    """
    def __init__(self, *children, x: int = None, y: int = None):
        self._x = 0
        self._y = 0
        self._child_items = list(children)
        self._opacity = 1.0
        super().__init__()
        
        if not self._child_items:
            self._x = x or 0
            self._y = y or 0
        else:
            self._sync_center()

        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

    def _sync_center(self):
        """Recalculate the center point based on current children positions."""
        if not self._child_items: return
        min_x = min(c.x for c in self._child_items)
        max_x = max(c.x for c in self._child_items)
        min_y = min(c.y for c in self._child_items)
        max_y = max(c.y for c in self._child_items)
        self._x = (min_x + max_x) // 2
        self._y = (min_y + max_y) // 2

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        dx = value - self._x
        self._x = value
        for c in self._child_items:
            c.x += dx

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        dy = value - self._y
        self._y = value
        for c in self._child_items:
            c.y += dy

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        for c in self._child_items:
            c.opacity = value

    def render(self, canvas):
        for c in self._child_items:
            if c.visible:
                c.render(canvas)

    def add_child(self, child: PObject):
        self._child_items.append(child)
        self._sync_center()
        return self


class VStack(Group):
    """Automatically arranges children in a vertical column."""
    def __init__(self, children, spacing: int = 10, align: str = "center", x: int = None, y: int = None):
        super().__init__(*children)
        self.spacing = spacing
        self.align = align
        self.arrange()
        if x is not None: self.x = x
        if y is not None: self.y = y

    def arrange(self):
        if not self._child_items: return
        current_y = 0
        for i, c in enumerate(self._child_items):
            h = getattr(c, 'height', 10)
            c.y = current_y
            current_y += h + self.spacing
            
            # X alignment (top-left semantics)
            if self.align == "center":
                c.x = 0
            elif self.align == "left":
                c.x = 0
            elif self.align == "right":
                w = getattr(c, 'width', 10)
                c.x = -w
                
        self._sync_center()


class HStack(Group):
    """Automatically arranges children in a horizontal row."""
    def __init__(self, children, spacing: int = 10, align: str = "center", x: int = None, y: int = None):
        super().__init__(*children)
        self.spacing = spacing
        self.align = align
        self.arrange()
        if x is not None: self.x = x
        if y is not None: self.y = y

    def arrange(self):
        if not self._child_items: return
        current_x = 0
        for i, c in enumerate(self._child_items):
            w = getattr(c, 'width', 10)
            c.x = current_x
            current_x += w + self.spacing
            
            # Y alignment (top-left semantics)
            if self.align == "center":
                c.y = 0
            elif self.align == "top":
                c.y = 0
            elif self.align == "bottom":
                h = getattr(c, 'height', 10)
                c.y = -h
                
        self._sync_center()
