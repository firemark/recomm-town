from itertools import product
from random import choice, choices, randint, random, shuffle
from dataclasses import dataclass
from typing import Iterable

from recomm_town.town.place import Place, Room
from recomm_town.human import Human, HumanInfo


vowels = "eiuoa"
consonants = "tpsdhjklmn"
syllabes = [c + v for c, v in product(consonants, vowels)]


def make_name() -> str:
    length = randint(2, 4)
    return "".join(choice(syllabes) for _ in range(length)).title()


@dataclass
class AvailablePlace:
    place: Place
    jobs: int


class AvailablePlaces:

    @classmethod
    def create(cls, jobs: set[Place]):
        return cls(AvailablePlace(p, len(p.rooms)) for p in jobs)

    def __init__(self, places: Iterable[AvailablePlace]) -> None:
        self.places = list(places)

    def extract(self, jobs: set[Place]) -> "AvailablePlaces":
        cls = type(self)
        return cls(p for p in self.places if p.place in jobs and p.jobs > 0)

    def find(self) -> Place | None:
        if not self.places:
            return None
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


def generate_people(
    houses,
    available_workplaces: AvailablePlaces,
    available_comms: AvailablePlaces,
    books,
) -> list[Human]:
    people = []
    for home in houses:
        family = []
        for room in home.rooms:
            workplace = available_workplaces.find()
            if workplace is None:
                raise RuntimeError("No jobs here.")
            human = _generate_human(home, room, workplace)
            _push_human_into_members(
                human,
                [workplace, available_comms.find()],
            )
            if books and random() > 0.95:
                human.library.append(choice(books))
            room.occupied_by = human
            family.append(human)
        _update_family_friendness(family)
        people += family

    shuffle(people)  # for random selecting people
    return people


def _generate_human(liveplace: Place, liveroom: Room, workplace: Place):
    info = HumanInfo(
        name=make_name(),
        liveplace=liveplace,
        liveroom=liveroom,
        workplace=workplace,
        speed=5.0 + random() * 5.0,
        stranger_trust_level=0.2 + random() * 0.1,
    )
    human = Human(info.liveroom.position, info)
    human.levels.money += random()
    human.levels.energy -= random() * 0.5
    human.levels.satiety -= random() * 0.3
    human.levels.fridge -= random() * 0.5
    return human


def _push_human_into_members(human: Human, places: list[Place | None]):
    for place in places:
        if place is None:
            continue
        place.members.append(human)


def _update_family_friendness(family: list[Human]):
    for a in family:
        for b in family:
            if a is b:
                continue
            a.update_friend_level(b, value=random() * 0.5)
            b.update_friend_level(b, value=random() * 0.5)
