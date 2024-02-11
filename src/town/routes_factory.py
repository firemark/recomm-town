from typing import Iterator
from .place import Place
from .routes import Routes


class RoutesFactory:
    places: list[Place]
    routes: Routes

    def __init__(self, places: list[Place]) -> None:
        self.places = places
        self.routes = Routes()

    def make(self) -> Routes:
        for place in self.places:
            new_routes = RoutesForSinglePlaceFactory(self.routes).make(place)
            for place_from, place_to, route in new_routes:
                self.routes[place_from, place_to] = route

        # z = sorted(self.routes.items(), key=lambda o: (o[0][0], len(o[1]), o[0][1]))
        # print("Total:", len(self.routes))
        # for (a, b), route in z:
        #     print(a, "=>", b, "::", " -> ".join(r.name for r in route))
        return self.routes


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
