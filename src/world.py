from random import choice, randint

from .human import Human
from .town.town import Town
from .town.place import PlaceFunction as PF
from .actions import Action, Move, Wait


class World:
    town: Town
    people: list[Human]

    def __init__(self, town: Town, people: list[Human]):
        self.town = town
        self.people = people

    def do_it(self, dt: float):
        for human in self.people:
            self.do_it_human(human, dt)

    def do_it_human(self, human: Human, dt: float):
        if not human.actions:
            place_from = self.town.find_nearest_place(human.position)
            route = None
            while not route:
                place_to = choice(self.town.places)
                if place_to.function is PF.CROSSROAD:
                    continue
                route = self.town.find_route(place_from, place_to)
            human.actions = [Move(place) for place in route]
            human.actions.append(Wait(randint(2, 5)))

        result = human.actions[0].do_it(human, dt)
        if result == "NEXT":
            human.actions.pop(0)
        elif isinstance(result, Action):
            human.actions.append(result)
