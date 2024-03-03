from typing import Optional

from recomm_town.town.place import Place, Way
from recomm_town.town.routes import Routes
from recomm_town.town.routes_factory import RoutesFactory
from recomm_town.common import Vec


class Town:
    places: list[Place]
    path: dict[tuple[Place, Place], Way]
    routes: Routes

    def __init__(self, places: list[Place]):
        self.places = places
        self.path = self.__create_ways_between_places(places)
        self.routes = RoutesFactory(places).make()
        self.boundaries = (
            Vec(min(p.box_start.x for p in places), min(p.box_start.y for p in places)),
            Vec(max(p.box_end.x for p in places), max(p.box_end.y for p in places)),
        )

    def __create_ways_between_places(self, places: list[Place]):
        path: dict[tuple[Place, Place], Way] = {}
        # places_to_go = places.copy()
        for place in places:
            # places_to_go.remove(place)
            for neighbor in place.neighborhood:
                # if neighbor not in places_to_go:
                #     continue
                path.update(self.__create_ways(place, neighbor))
        return path

    def __create_ways(self, a: Place, b: Place) -> dict[tuple[Place, Place], Way]:
        ap = a.position
        bp = b.position
        direction = (ap - bp).normalize() * 25.0
        left_shift = Vec(direction.y, -direction.x)
        right_shift = Vec(-direction.y, direction.x)
        way_ab = Way([ap + right_shift, bp + right_shift])
        way_ba = Way([bp + left_shift, ap + left_shift])
        return {
            (a, b): way_ab,
            (b, a): way_ba,
        }

    def find_nearest_place(self, position: Vec) -> Place:
        return min(
            self.places,
            key=lambda place: (place.position - position).length_squared(),
        )

    def find_route(self, place_from: Place, place_to: Place) -> Optional[list[Place]]:
        if place_from is place_to:
            return []
        route = self.routes.get(place_from, place_to)
        return route and [place_from, *route, place_to]
