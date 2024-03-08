from enum import Enum
from dataclasses import dataclass, field
from functools import total_ordering
from random import random
from typing import Iterable, Self

from recomm_town.common import Book, Rotate, Trivia, Vec
from recomm_town.human import Human


class PlaceFunction(Enum):
    CROSSROAD = 0
    HOME = 1
    WORK = 2
    SHOP = 3
    ENTERTAIMENT = 4
    COMMUNITY = 5


@dataclass
class LocalRoom:
    local_position: Vec
    local_path: list[Vec]
    rotation: float = 0.0


@dataclass
class Room:
    position: Vec
    path: list[Vec]
    occupied_by: "Human | None" = None
    owner: "Human | None" = None
    rotation: float = 0.0


@total_ordering
class Place:
    name: str
    position: Vec
    function: PlaceFunction
    neighborhood: set[Self]
    rooms: list[Room]
    room_size: float
    box_start: Vec
    box_end: Vec
    learn_trivias: list[Trivia]
    talk_trivias: set[Trivia]
    talk_trivias_order: float
    books: list[Book]
    members: list[Human]

    def __init__(
        self,
        name: str,
        title: str,
        position: Vec,
        function: PlaceFunction,
        rooms: Iterable[LocalRoom] | None = None,
        room_size: float = 80.0,
        room_padding: float = 10.0,
        learn_trivias: list[Trivia] | None = None,
        talk_trivias: list[Trivia] | None = None,
        talk_trivias_order: float = 0.0,
        books: list[Book] | None = None,
        rotation: float = 0.0,
    ):
        self.name = name
        self.title = title
        self.position = position
        self.function = function
        self.neighborhood = set()
        self.room_size = room_size
        self.room_padding = room_padding
        self.learn_trivias = learn_trivias or []
        self.talk_trivias = set(talk_trivias) if talk_trivias else set()
        self.talk_trivias_order = talk_trivias_order
        self.books = books or []
        self.members = []
        self.rotation = rotation

        rot = Rotate(self.rotation)
        s = room_size + room_padding
        p = self.position
        rooms = list(rooms) if rooms else []
        self.rooms = [
            Room(
                position=p + rot(room.local_position * s),
                path=[p + rot(vec * s) for vec in room.local_path],
                rotation=self.rotation + room.rotation,
            )
            for room in rooms
        ]

        if rooms:
            h = s / 2
            x_min = min(room.local_position.x for room in rooms)
            y_min = min(room.local_position.y for room in rooms)
            x_max = max(room.local_position.x for room in rooms)
            y_max = max(room.local_position.y for room in rooms)
            local_start = Vec(x_min, y_min) * s - h
            local_end = Vec(x_max, y_max) * s + h
        else:
            local_start = -Vec(100.0, 100.0)
            local_end = Vec(100.0, 100.0)
        self.box_start = p + local_start
        self.box_end = p + local_end
        self.boundaries = (
            p - abs(rot(local_start)),
            p + abs(rot(local_end)),
        )

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f"Place[{self.name}]"

    def connect(self, *others: Self):
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
class Invite:
    place: Place
    period: float
    priority: float = 1.0
    lifetime: float = field(init=False)

    def __post_init__(self):
        self.lifetime = self.period

    def __hash__(self) -> int:
        return hash(self.place)

    def __repr__(self):
        return f"Invite[{self.place.name}]"

    def do_it(self, dt):
        self.lifetime -= dt
        if self.lifetime < 0.0:
            self.lifetime = self.period
            self._invite()

    def _invite(self):
        place = self.place
        prior = self.priority
        for member in place.members:
            if random() > prior:
                continue
            member.invite_to_place(place)


@dataclass
class Way:
    points: list[Vec]
