from math import atan2, pi
from typing import Iterator

from recomm_town.town.place import Place
from recomm_town.town.routes import Routes


class RoutesFactory:
    places: list[Place]
    routes: Routes
    _len_cache: dict[tuple[Place, Place], float]

    def __init__(self, places: list[Place]) -> None:
        self.places = places
        self.routes = Routes()
        self._len_cache = {}

    def make(self) -> Routes:
        for place in self.places:
            new_routes = RoutesForSinglePlaceFactory(self.routes).make(place)
            for place_from, place_to, new_route in new_routes:
                new_route_len = self._len(new_route)
                old_route_len = self._len_cache.get((place_from, place_to), float("inf"))
                if old_route_len < new_route_len:
                    continue

                self._len_cache[place_from, place_to] = new_route_len
                self.routes[place_from, place_to] = new_route

        # z = sorted(self.routes.items(), key=lambda o: (o[0][0], len(o[1]), o[0][1]))
        # print("Total:", len(self.routes))
        # for (a, b), route in z:
        #     print(a, "=>", b, "::", " -> ".join(r.name for r in route))
        return self.routes

    def _len(self, places: list[Place]) -> float:
        length = 0.0
        for i in range(len(places) - 1):
            ap = places[i].position
            bp = places[i + 1].position
            diff = ap - bp
            length += diff.length_squared()
        return length


class RoutesForSinglePlaceFactory:
    routes: Routes
    visited: set[Place]

    def __init__(self, routes: Routes) -> None:
        self.routes = routes
        self.visited = set()

    def make(self, place_from: Place) -> Iterator[tuple[Place, Place, list[Place]]]:
        self.visited.add(place_from)
        for place_to in place_from.neighborhood:
            if place_to in self.visited:
                continue

            if route := self.routes.get(place_from, place_to):
                yield place_from, place_to, route
                continue

            yield place_from, place_to, []
            for _, place, route in self.make(place_to):
                yield place_from, place, [place_to] + route
