from enum import Enum
from dataclasses import dataclass
from functools import total_ordering
from typing import Iterable

from recomm_town.common import Trivia, Vec
from recomm_town.human import Human


class PlaceFunction(Enum):
    CROSSROAD = 0
    HOME = 1
    WORK = 2
    SHOP = 3
    ENTERTAIMENT = 4


@dataclass
class LocalRoom:
    local_position: Vec
    local_path: list[Vec]


@dataclass
class Room:
    position: Vec
    path: list[Vec]
    occupied_by: "Human | None" = None
    owner: "Human | None" = None


@total_ordering
class Place:
    name: str
    position: Vec
    function: PlaceFunction
    neighborhood: set["Place"]
    rooms: list[Room]
    room_size: float
    box_start: Vec
    box_end: Vec
    trivias: list[Trivia]

    def __init__(
        self,
        name: str,
        position: Vec,
        function: PlaceFunction,
        rooms: Iterable[LocalRoom] | None = None,
        room_size: float = 80.0,
        room_padding: float = 10.0,
        trivias: list[Trivia] | None = None,
    ):
        self.name = name
        self.position = position
        self.function = function
        self.neighborhood = set()
        self.room_size = room_size
        self.room_padding = room_padding
        self.trivias = trivias or []

        s = room_size + room_padding
        self.rooms = [
            Room(
                position=self.position + room.local_position * s,
                path=[self.position + vec * s for vec in room.local_path],
            )
            for room in rooms or []
        ]

        if self.rooms:
            h = s / 2
            x_min = min(room.position.x for room in self.rooms)
            y_min = min(room.position.y for room in self.rooms)
            x_max = max(room.position.x for room in self.rooms)
            y_max = max(room.position.y for room in self.rooms)
            self.box_start = Vec(x_min, y_min) - h
            self.box_end = Vec(x_max, y_max) + h
        else:
            self.box_start = self.position - 50.0
            self.box_end = self.position + 50.0

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
