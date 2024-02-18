from typing import NamedTuple


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


class Trivia(NamedTuple):
    category: str
    name: str


class Book(NamedTuple):
    trivia: Trivia