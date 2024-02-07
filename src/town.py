from enum import Enum
from dataclasses import dataclass

from .common import Vec


class PlaceFunction(Enum):
    CROSSROAD = 0
    HOME = 1
    WORK = 2
    SHOP = 3
    MUSEUM = 4


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


@dataclass
class Way:
    a: Place
    b: Place

    def __repr__(self):
        return f"Way[{self.a.name:<20} <=> {self.b.name:>20}]"


class Town:
    places: set[Place]
    path: list[Way]
    place_to_way: dict[Place, Way]

    def __init__(self, places: set[Place]):
        self.places = places
        self.path = []
        self.place_to_way = {}

        places_to_go = places.copy()
        for place in places:
            places_to_go.remove(place)
            for neighbor in place.neighborhood:
                if neighbor not in places_to_go:
                    continue
                if place.name >= neighbor.name:
                    way = Way(a=place, b=neighbor)
                else:
                    way = Way(a=neighbor, b=place)
                self.path.append(way)
                self.place_to_way[place] = way
                self.place_to_way[neighbor] = way
