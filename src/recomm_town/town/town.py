from typing import Optional

from recomm_town.town.place import Place, Way
from recomm_town.town.routes import Routes
from recomm_town.town.routes_factory import RoutesFactory
from recomm_town.common import Vec


class Town:
    places: list[Place]
    path: list[Way]
    place_to_way: dict[Place, Way]
    routes: Routes

    def __init__(self, places: list[Place]):
        self.places = places
        self.path, self.place_to_way = self.__create_ways_between_places(places)
        self.routes = RoutesFactory(places).make()

    def __create_ways_between_places(self, places: list[Place]):
        path: list[Way] = []
        place_to_way: dict[Place, Way] = {}
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
