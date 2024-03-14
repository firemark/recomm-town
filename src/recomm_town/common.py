from dataclasses import dataclass
from functools import cache
from math import sin, cos, radians
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

    def __abs__(self) -> "Vec":
        return Vec(abs(self.x), abs(self.y))

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
    def from_hex(cls, x: str) -> Self:
        assert x[0] == "#"
        r = int(x[1:3], 16)
        g = int(x[3:5], 16)
        b = int(x[5:7], 16)
        return cls.from_pyglet(r, g, b)

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

    def mix(self, other: "Color", level: float) -> "Color":
        level = min(max(level, 0.0), 1.0)
        return self * level + other * (1.0 - level)

    @cache
    def to_pyglet(self):
        r, g, b = self
        return (
            int(min(max(r, 0.0), 1.0) * 255),
            int(min(max(g, 0.0), 1.0) * 255),
            int(min(max(b, 0.0), 1.0) * 255),
        )

    @cache
    def to_pyglet_alpha(self, a=1.0):
        r, g, b = self
        return (
            int(min(max(r, 0.0), 1.0) * 255),
            int(min(max(g, 0.0), 1.0) * 255),
            int(min(max(b, 0.0), 1.0) * 255),
            int(min(max(a, 0.0), 1.0) * 255),
        )


@dataclass(frozen=True)
class Trivia:
    category: str
    name: str
    chunks: int = 4
    popularity: float = 1.0
    forgetting_level: float = 1e-4

    def get_chunk(self, id: int) -> "TriviaChunk":
        return TriviaChunk(self, id)


class TriviaChunk(NamedTuple):
    trivia: Trivia
    id: int


class Book(NamedTuple):
    trivia: Trivia


class Rotate:
    def __init__(self, rotation: float):
        self.rotation = rotation
        self.rotation_rad = radians(rotation)
        self.sin = sin(self.rotation_rad)
        self.cos = cos(self.rotation_rad)

    def __call__(self, p: Vec) -> Vec:
        s = self.sin
        c = self.cos
        return Vec(
            x=p.x * c - p.y * s,
            y=p.x * s + p.y * c,
        )
