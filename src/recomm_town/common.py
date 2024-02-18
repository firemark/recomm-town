from typing import NamedTuple, Self


class Vec(NamedTuple):
    x: float
    y: float

    def __add__(self, other) -> "Vec":
        if isinstance(other, (float, int)):
            return Vec(self.x + other, self.y + other)
        if isinstance(other, Vec):
            return Vec(self.x + other.x, self.y + other.y)
        return NotImplemented

    def __sub__(self, other) -> "Vec":
        if isinstance(other, (float, int)):
            return Vec(self.x - other, self.y - other)
        if isinstance(other, Vec):
            return Vec(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __mul__(self, other) -> "Vec":
        if isinstance(other, (float, int)):
            return Vec(self.x * other, self.y * other)
        return NotImplemented

    def __neg__(self) -> "Vec":
        return Vec(-self.x, -self.y)

    def normalize(self) -> "Vec":
        max_abs = max(abs(self.x), abs(self.y))
        assert max_abs != 0.0
        return Vec(self.x / max_abs, self.y / max_abs)

    def length(self) -> float:
        return (self.x**2 + self.y**2) ** (1 / 2)

    def length_squared(self) -> float:
        return self.x**2 + self.y**2


class Color(NamedTuple):
    r: float
    g: float
    b: float

    @classmethod
    def from_pyglet(cls, r: float, g: float, b: float) -> Self:
        return cls(r / 255, g / 255, b / 255)

    def __add__(self, other) -> "Color":
        if isinstance(other, (float, int)):
            return Color(self.r + other, self.g + other, self.b + other)
        if isinstance(other, Color):
            return Color(self.r + other.r, self.g + other.g, self.b + other.b)
        return NotImplemented

    def __sub__(self, other) -> "Color":
        if isinstance(other, (float, int)):
            return Color(self.r - other, self.g - other, self.b - other)
        if isinstance(other, Color):
            return Color(self.r - other.r, self.g - other.g, self.b - other.b)
        return NotImplemented

    def __mul__(self, other) -> "Color":
        if isinstance(other, (float, int)):
            return Color(self.r * other, self.g * other, self.b * other)
        return NotImplemented

    def __neg__(self) -> "Color":
        return Color(-self.r, -self.g, -self.b)

    def normalize(self) -> "Color":
        max_abs = max(self.r, self.g, self.b)
        assert max_abs != 0.0
        return Color(self.r / max_abs, self.g / max_abs, self.b / max_abs)

    def to_pyglet(self):
        r, g, b = self
        return (
            min(max(r, 0.0), 1.0) * 255,
            min(max(g, 0.0), 1.0) * 255,
            min(max(b, 0.0), 1.0) * 255,
        )


class Trivia(NamedTuple):
    category: str
    name: str


class Book(NamedTuple):
    trivia: Trivia
