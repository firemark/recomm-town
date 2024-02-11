from enum import Enum
from dataclasses import dataclass
from functools import total_ordering

from ..common import Vec


class PlaceFunction(Enum):
    CROSSROAD = 0
    HOME = 1
    WORK = 2
    SHOP = 3
    MUSEUM = 4


@total_ordering
class Place:
    name: str
    position: Vec
    function: PlaceFunction
    neighborhood: set["Place"]

    def __init__(self, name: str, position: Vec, function: PlaceFunction):
        self.name = name
        self.position = position
        self.function = function
        self.neighborhood = set()

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"Place[{self.name}]"

    def connect(self, *others: "Place"):
        for other in others:
            self.neighborhood.add(other)
            other.neighborhood.add(self)

    def __eq__(self, other):
        if not isinstance(other, Place):
            return NotImplemented
        return self.name == other.name

    def __lt__(self, other):
        if not isinstance(other, Place):
            return NotImplemented
        return self.name < other.name


@dataclass
class Way:
    a: Place
    b: Place

    def __repr__(self):
        return f"Way[{self.a.name:<20} <=> {self.b.name:>20}]"
