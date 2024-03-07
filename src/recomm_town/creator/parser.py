from itertools import chain
from pathlib import Path
from random import choices, shuffle
import re
import yaml

from recomm_town.common import Book, Trivia, Vec
from recomm_town.human import Human
from recomm_town.program import Program
from recomm_town.town import Town, Place, PlaceFunction, LocalRoom
from recomm_town.world import World, WorldLevels
from recomm_town.creator.helpers import (
    AvailableWorkplaces,
    generate_people,
    make_flat_rooms,
    make_grid_rooms,
    make_round_rooms,
)


class WorldParser:
    ROOM_FACTORIES = {
        "flat": make_flat_rooms,
        "grid": make_grid_rooms,
        "round": make_round_rooms,
    }

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.places: dict[str, set[Place]] = {}
        self.place_positions: dict[str, Vec] = {}
        self.trivias: dict[str, list[Trivia]] = {}
        self.people: list[Human] = []

    def load(self):
        with open(self.path) as file:
            config = yaml.safe_load(file)

        for trivias_path in config["trivias"]:
            self._load_trivias(self.path.parent / trivias_path)

        for place in config["places"]:
            self._load_place(place, {})

        for connection in config["connections"]:
            self._load_connection(connection)

        available_workplaces = AvailableWorkplaces.create(
            set(
                chain.from_iterable(
                    (job for job in self._find_places(people["jobs"]))
                    for people in config["people"]
                )
            )
        )

        for people in config["people"]:
            self._load_people(people, available_workplaces)

        world_config = config.get("world", {})
        self.radio_program = self._load_program(world_config.get("radio", {}))
        self.tv_program = self._load_program(world_config.get("tv", {}))

        levels = world_config.get("levels", {})
        forgetting = world_config.get("forgetting", {})
        self.levels = WorldLevels(
            neighbor_range=world_config.get(
                "neighbor-range", WorldLevels.neighbor_range
            ),
            forgetting_tick=forgetting.get("tick", WorldLevels.forgetting_tick),
            forgetting_factor=forgetting.get("factor", WorldLevels.forgetting_factor),
            learning=levels.get("learning", WorldLevels.learning),
            teaching=levels.get("teaching", WorldLevels.teaching),
            reading=levels.get("reading", WorldLevels.reading),
            talking=levels.get("talking", WorldLevels.talking),
            program=levels.get("program", WorldLevels.program),
            warmup_time=levels.get("warmup-time", WorldLevels.warmup_time),
        )

    def create_world(self) -> World:
        shuffle(self.people)
        places = chain.from_iterable(self.places.values())
        places = list(places)
        shuffle(places)

        return World(
            town=Town(places),
            people=self.people,
            tv_program=self.tv_program,
            radio_program=self.radio_program,
            levels=self.levels,
        )

    def _load_program(self, program) -> Program:
        trivias = self._find_trivias(program.get("program")) or []
        lifetime = program.get("lifetime", 15)
        start_after = program.get("start-after", 0.0)
        return Program(trivias, lifetime, start_after)

    def _load_trivias(self, trivia_path: Path):
        with open(trivia_path) as file:
            config = yaml.safe_load(file)

        for group_name, categories in config.items():
            group = self.trivias.get(group_name)
            if group is None:
                group = []
                self.trivias[group_name] = group
            for category in categories:
                args = dict(
                    category=category["category"],
                    chunks=category.get("chunks", Trivia.chunks),
                    forgetting_level=category.get(
                        "forgetting-level", Trivia.forgetting_level
                    ),
                    popularity=category.get("popularity", Trivia.popularity),
                )
                raw_trivias = category["trivias"]
                choice = category.get("choice")
                if choice is not None:
                    raw_trivias = choices(raw_trivias, k=choice)
                group += [Trivia(name=name, **args) for name in raw_trivias]

            self.trivias[group_name] = group

    def _load_place(self, place, prev_params, prefix="") -> set[Place]:
        name = prefix + place["name"]
        prev_position = prev_params.pop("position", None)
        position = self._load_position(place.get("position"), prev_position)

        params = {
            "function": place.get("function"),
            "rotation": place.get("rotation"),
            "title": place.get("title"),
            "rooms": place.get("rooms"),
            "room-size": place.get("room-size"),
            "room-padding": place.get("room-padding"),
            "learn_trivias": place.get("trivias-to-learn"),
            "talk_trivias": place.get("trivias-to-talk"),
            "talk_trivias_order": place.get("trivias-to-talk-order"),
            "position": position,
        }
        new_params = prev_params | {k: v for k, v in params.items() if v is not None}

        if position is not None:
            self.place_positions[name] = position

        if "places" not in place:
            places = {self._create_place(name, new_params)}
        else:
            places = set()
            for child in place["places"]:
                places |= self._load_place(child, new_params.copy(), f"{name}.")

        self.places[name] = places
        return places

    def _create_place(self, name, params) -> Place:
        return Place(
            name=name,
            title=params["title"],
            position=params["position"],
            rotation=params.get("rotation", 0.0),
            function=PlaceFunction[params["function"]],
            rooms=self._create_rooms(params.get("rooms")),
            room_size=params.get("room-size", 80.0),
            room_padding=params.get("room-padding", 10.0),
            learn_trivias=self._find_trivias(params.get("learn_trivias")),
            talk_trivias=self._find_trivias(params.get("talk_trivias")),
            talk_trivias_order=params.get("talk_trivias_order", 0.0),
            books=self._find_books(params.get("books")),
        )

    def _find_trivias(self, trivias_group_name: str | None) -> list[Trivia] | None:
        if trivias_group_name is None:
            return None
        return self.trivias[trivias_group_name]

    def _find_books(self, trivias_group_name: str | None) -> list[Book] | None:
        trivias = self._find_trivias(trivias_group_name)
        if trivias is None:
            return None
        return [Book(t) for t in trivias]

    def _load_position(self, position, prev_vec) -> Vec | None:
        match position:
            case [x, y]:
                vec = Vec(float(x), float(y))
            case str():
                vec = self.place_positions[position]
            case None:
                vec = None
            case _:
                raise RuntimeError(f"wrong format of position: {position!r}")
        if vec is None or prev_vec is None:
            return vec
        return vec + prev_vec

    def _create_rooms(self, room_pattern: str | None) -> list[LocalRoom] | None:
        if room_pattern is None:
            return None
        match = re.match(r"([\w_]+)\(([\w\s,]+)\)", room_pattern)
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

        neighborhood = self._find_places(connection["with"])

        place = next(iter(places))
        place.connect(*neighborhood)

    def _load_people(self, config, available_workplaces: AvailableWorkplaces):
        jobs = self._find_places(config["jobs"])
        self.people += generate_people(
            houses=self._find_places(config["houses"]),
            available_workplaces=available_workplaces.extract(jobs),
            books=self._find_books(config.get("books")),
        )

    def _find_places(self, obj: str | list[str]) -> set[Place]:
        places = set()
        if isinstance(obj, str):
            obj = [obj]

        for name in obj:
            try:
                places |= self.places[name]
            except KeyError:
                raise RuntimeError(f"place {name!r} not found!")

        return places
