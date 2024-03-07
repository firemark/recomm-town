from itertools import chain, product
from random import choice, choices, randint, random, shuffle
from dataclasses import dataclass
from typing import Iterable

from recomm_town.common import Book, Trivia, Vec
from recomm_town.draw import Draw
from recomm_town.town.town import Town
from recomm_town.town.place import LocalRoom, Place, PlaceFunction as PF
from recomm_town.human import Human, HumanInfo


def make_flat_rooms(n, m):
    max_lvl = m * 2 - 4

    for y in range(-1, m * 2 - 1, 2):
        lvl = min(max_lvl, y + 1)
        yield from (
            LocalRoom(Vec(-x, +y), [Vec(0, lvl), Vec(-x, lvl)])
            for x in chain.from_iterable((-x, x) for x in range(+1, n + 1))
        )


def make_grid_rooms(n):
    return (
        LocalRoom(Vec(x, y), [Vec(x + hall, 0), Vec(x + hall, y)])
        for x, y, hall in chain.from_iterable(
            [(-x, -y, +0.5), (-x, +y, +0.5), (+x, +y, -0.5), (+x, -y, -0.5)]
            for x in range(1, n + 1)
            for y in range(1, n + 1)
        )
    )


def make_round_rooms(n, m):
    return make_grid_rooms(n)


vowels = "eiuoa"
consonants = "tpsdhjklmn"
syllabes = [c + v for c, v in product(consonants, vowels)]


def make_name() -> str:
    length = randint(2, 4)
    return "".join(choice(syllabes) for _ in range(length)).title()


def generate_people(houses, available_workplaces, books) -> list[Human]:
    people = []
    for home in houses:
        family = []
        for room in home.rooms:
            info = HumanInfo(
                name=make_name(),
                liveplace=home,
                liveroom=room,
                workplace=available_workplaces.find(),
                speed=5.0 + random() * 5.0,
                stranger_trust_level=0.2 + random() * 0.1,
            )
            human = Human(info.liveroom.position, info)
            human.levels.money += random()
            human.levels.energy -= random() * 0.5
            human.levels.satiety -= random() * 0.3
            human.levels.fridge -= random() * 0.5
            if random() > 0.95:
                human.library.append(choice(books))
            room.occupied_by = human
            family.append(human)
        _update_family_friendness(family)
        people += family

    shuffle(people)  # for random selecting people
    return people


def _update_family_friendness(family: list[Human]):
    for a in family:
        for b in family:
            if a is b:
                continue
            a.update_friend_level(b, value=random() * 0.5)
            b.update_friend_level(b, value=random() * 0.5)


@dataclass
class AvailableWorkplace:
    place: Place
    jobs: int


class AvailableWorkplaces:

    @classmethod
    def create(cls, jobs: set[Place]):
        return cls(AvailableWorkplace(p, len(p.rooms)) for p in jobs)

    def __init__(self, places: Iterable[AvailableWorkplace]) -> None:
        self.places = list(places)

    def extract(self, jobs: set[Place]) -> "AvailableWorkplaces":
        cls = type(self)
        return cls(p for p in self.places if p.place in jobs and p.jobs > 0)

    def find(self) -> Place:
        if not self.places:
            raise RuntimeError("No jobs here.")
        available_workspaces = choices(
            self.places,
            weights=[w.jobs for w in self.places],
        )
        available_workspace = available_workspaces[0]
        available_workspace.jobs -= 1
        if available_workspace.jobs <= 0:
            index = self.places.index(available_workspace)
            self.places.pop(index)
        return available_workspace.place
