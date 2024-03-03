from pprint import pprint
import re
import yaml

from recomm_town.common import Vec
from recomm_town.town import Place, PlaceFunction, LocalRoom
from recomm_town.creator.helpers import make_flat_rooms, make_grid_rooms


class WorldParser:
    ROOM_FACTORIES = {
        "flat": make_flat_rooms,
        "grid": make_grid_rooms,
    }

    def __init__(self, path: str):
        self.path = path
        self.places: dict[str, set[Place]] = {}
        self.place_positions: dict[str, Vec] = {}

    def load(self):
        with open(self.path) as file:
            config = yaml.safe_load(file)

        for place in config["places"]:
            self._load_place(place, {})

        for connection in config["connections"]:
            self._load_connection(connection)

    def _load_place(self, place, prev_params, prefix="") -> set[Place]:
        name = prefix + place["name"]
        prev_position = prev_params.pop("position", None)
        position = self._load_position(place.get("position"), prev_position)

        params = {
            "function": place.get("function"),
            "rotation": place.get("rotation"),
            "title": place.get("title"),
            "room": place.get("room"),
            "room-size": place.get("room-size"),
            "room-padding": place.get("room-padding"),
            "position": position,
        }
        new_params = prev_params | {k: v for k, v in params.items() if v is not None}

        if position is not None:
            self.place_positions[name] = position

        if "places" not in place:
            places = {self._create_place(new_params)}
        else:
            places = set()
            for child in place["places"]:
                places |= self._load_place(child, new_params, f"{name}.")

        self.places[name] = places
        return places


    def _create_place(self, params) -> Place:
        return Place(
            name=params["title"],
            position=params["position"],
            rotation=params.get("rotation", 0.0),
            function=PlaceFunction[params["function"]],
            rooms=self._create_rooms(params.get("rooms")),
            room_size=params.get("room-size", 80.0),
            room_padding=params.get("room-padding", 10.0),
            # trivias=
            # books=
        )

    def _load_position(self, position, prev_position) -> Vec | None:
        match position:
            case [x, y]:
                vec = Vec(float(x), float(y))
            case str(position_name):
                vec = self.place_positions[position_name]
            case None:
                vec = None
            case _:
                raise RuntimeError(f"wrong format of position: {position!r}")
        if position is None or prev_position is None:
            return vec
        return vec + prev_position

    def _create_rooms(self, room_pattern: str | None) -> list[LocalRoom] | None:
        if room_pattern is None:
            return None
        match = re.match(r"([\w_]+)\([\w\s,]+\)", room_pattern)
        if match is None:
            raise RuntimeError(f"Wrong room format: {room_pattern!r}")
        name, raw_args = match.groups()
        factory = self.ROOM_FACTORIES[name]
        args = [int(x.strip()) for x in raw_args.strip().split(",")]
        return factory(*args)

    def _load_connection(self, connection):
        name = connection["name"]
        try:
            places = self.places[name]
        except KeyError:
            raise RuntimeError(f"place {name!r} not found!")
        if len(places) > 1:
            raise RuntimeError(f"place {name!r} is not a single place!")

        connections = connection["with"]
        if isinstance(connections, str):
            connections = [connections]

        neighborhood = set()
        for neighbor_name in connections:
            try:
                neighborhood |= self.places[neighbor_name]
            except KeyError:
                raise RuntimeError(f"place {neighbor_name!r} not found!")

        place = next(iter(places))
        place.connect(*neighborhood)
