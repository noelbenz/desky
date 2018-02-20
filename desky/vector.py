
class Vec2:
    """Model a 2-Dimension vector and provide some basic operations."""

    def __init__(self, x=0, y=0):
        """Construct a 2D vector from x and y components."""
        self.x = x
        self.y = y

    @property
    def width(self):
        """Return the x component."""
        return self.x

    @width.setter
    def width(self, width):
        """Set the x component."""
        self.x = width

    @property
    def height(self):
        """Return the y component."""
        return self.y

    @height.setter
    def height(self, height):
        """Set the y component."""
        self.y = height

    def copy(self):
        """Return a copy of this vector."""
        return Vec2(self.x, self.y)

    def __add__(self, rhs):
        """Return the sum of two vectors as a new vector."""
        return Vec2(self.x + rhs.x, self.y + rhs.y)

    def __sub__(self, rhs):
        """Return the difference between two vectors as a new vector."""
        return Vec2(self.x - rhs.x, self.y - rhs.y)

    def __mul__(self, rhs):
        """Return the results of a scalar product as a new vector."""
        return Vec2(self.x * rhs, self.y * rhs)

    def __mod__(self, rhs):
        """Return the results of a scalar modulo as a new vector."""
        return Vec2(self.x % rhs, self.y % rhs)

    def __floordiv__(self, rhs):
        """Return the results of a scalar floored division as a new vector."""
        return Vec2(self.x // rhs, self.y // rhs)

    def __truediv__(self, rhs):
        """Return the results of a scalar division as a new vector."""
        return Vec2(self.x / rhs, self.y / rhs)

    def __neg__(self):
        """Return the negation of this vector as a new vector."""
        return Vec2(-self.x, -self.y)

    def __str__(self):
        """Return a string representation of this vector."""
        return "<{}, {}>".format(self.x, self.y)

    def __eq__(self, rhs):
        return self.x == rhs.x and self.y == rhs.y

    def dot(self, rhs):
        """Return the result of a dot product between two vectors."""
        return self.x * rhs.x + self.y * rhs.y

    def length(self):
        """Compute and return the length."""
        return pow(self.dot(self), 0.5)

    def normalize(self):
        """Normalize this vector in place and return itself."""
        length = self.length()
        self.x /= length
        self.y /= length
        return self

    def normalized(self):
        """Return a normalized copy of this vector."""
        return self.copy().normalize()

    def as_tuple(self):
        """Return the tuple (x-component, y-component)"""
        return (self.x, self.y)

