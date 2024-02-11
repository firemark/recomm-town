from enum import Enum
from dataclasses import dataclass
from functools import total_ordering
from typing import Optional

from .common import Vec


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


class Town:
    places: set[Place]
    path: list[Way]
    place_to_way: dict[Place, Way]
    routes: dict[tuple[Place, Place], list[Vec]]

    def __init__(self, places: set[Place]):
        self.places = places
        self.path, self.place_to_way = self.__create_ways_between_places(places)
        self.routes = self.__create_routes(places)

    def __create_ways_between_places(self, places: set[Place]):
        path: list[Way] = []
        place_to_way: dict[Place, Way]  = {}
        places_to_go = places.copy()
        for place in places:
            places_to_go.remove(place)
            for neighbor in place.neighborhood:
                if neighbor not in places_to_go:
                    continue
                if place < neighbor:
                    way = Way(a=place, b=neighbor)
                else:
                    way = Way(a=neighbor, b=place)
                path.append(way)
                place_to_way[place] = way
                place_to_way[neighbor] = way
        return path, place_to_way

    def __create_routes(self, places: set[Place]):
        routes: dict[tuple[Place, Place], list[Place]] = {}
        for place in places:
            new_routes = self.__create_routes_greedy(place, set(), routes)
            for place_from, place_to, route in new_routes:
                if place_from >= place_to:
                    place_from, place_to = place_to, place_from 
                    route = route[::-1]
                routes[place_from, place_to] = route
        
        # z = sorted(routes.items(), key=lambda o: (o[0][0], len(o[1]), o[0][1]))
        # print("Total:", len(routes))
        # for (a, b), route in z:
        #     print(a, "=>", b, "::", " -> ".join(r.name for r in route))
        return routes

    def __create_routes_greedy(self, place_from: Place, visited: set[Place], cache_routes):
        if place_from in visited:
            return
        visited.add(place_from)

        for place_to in place_from.neighborhood:
            if place_to in visited:
                continue
            if place_from < place_to:
                if route := cache_routes.get((place_from, place_to)):
                    yield place_from, place_to, route
                    continue
            else:
                if route := cache_routes.get((place_to, place_from)):
                    yield place_from, place_to, route[::-1]
                    continue
            
            yield place_from, place_to, []
            routes = self.__create_routes_greedy(place_to, visited, cache_routes)
            for _, place, route in routes:
                yield place_from, place, [place_to] + route
    

    def find_route(self, place_from: Place, place_to: Place) -> list[Place]:
        if place_from is place_to:
            return []
        if place_from < place_to:
            route = self.routes[place_from, place_to]
        else:
            route = self.routes[place_to, place_from][::-1]
        return [place_from, *route, place_to]
