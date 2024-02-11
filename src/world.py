from random import choice, randint, random

from .human import Activity, Emotion, Human
from .town.town import Town
from .town.place import Place, Room, PlaceFunction as PF
from .actions import Action, Move, Wait, ChangeActivity, UpdateLevel


class World:
    town: Town
    people: list[Human]
    simulation_speed: float

    def __init__(self, town: Town, people: list[Human]):
        self.town = town
        self.people = people
        self.simulation_speed = 10.0

    def do_it(self, dt: float):
        for human in self.people:
            self._do_it_human(human, dt * self.simulation_speed)

    def _do_it_human(self, human: Human, dt: float):
        if not human.actions:
            human.actions = self._make_new_actions(human)

        result = human.actions[0].do_it(human, dt)
        if result == "NEXT":
            human.actions.pop(0)
        elif isinstance(result, Action):
            human.actions[0] = result

    def _make_new_actions(self, human: Human) -> list[Action]:
        emotion = human.measure_emotion()

        if emotion == Emotion.POOR:
            return [
                ChangeActivity(Activity.MOVE),
                *self._make_move_action_by_place(human, human.info.workplace),
                ChangeActivity(Activity.WORK),
                Wait(randint(20, 30)),
                UpdateLevel("money", 0.5 + random() * 0.3),
                UpdateLevel("tiredness", 0.5 + random() * 0.2),
                UpdateLevel("fullness", -0.5 + random() * 0.3),
            ]
        if emotion == Emotion.EMPTY_FRIDGE:
            return [
                ChangeActivity(Activity.MOVE),
                *self._make_move_action_by_function(human, PF.SHOP),
                ChangeActivity(Activity.SHOP),
                Wait(randint(5, 10)),
                UpdateLevel("fridge", 1.0 - random() * 0.2),
                UpdateLevel("money", -0.3 - random() * 0.1),
                UpdateLevel("tiredness", 0.2 + random() * 0.1),
                UpdateLevel("fullness", -0.1 - random() * 0.1),
            ]
        if emotion == Emotion.HUNGRY:
            return [
                ChangeActivity(Activity.MOVE),
                *self._make_move_action_by_place(human, human.info.liveplace),
                UpdateLevel("fridge", -0.4 - random() * 0.2),
                ChangeActivity(Activity.EAT),
                Wait(randint(5, 10)),
                UpdateLevel("fullness", 1.0 - random() * 0.2),
                UpdateLevel("tiredness", 0.1 + random() * 0.1),
            ]
        if emotion == Emotion.TIRED:
            return [
                ChangeActivity(Activity.MOVE),
                *self._make_move_action_by_place(human, human.info.liveplace),
                ChangeActivity(Activity.SLEEP),
                Wait(randint(10, 20)),
                UpdateLevel("tiredness", -1.0),
                UpdateLevel("fullness", -0.4 - random() * 0.2),
            ]

        r = random()

        if r > 0.5:
            return [
                ChangeActivity(Activity.MOVE),
                *self._make_move_action_by_function(human, PF.ENTERTAIMENT),
                ChangeActivity(Activity.ENJOY),
                Wait(randint(5, 10)),
                UpdateLevel("money", -0.1 - random() * 0.2),
                UpdateLevel("tiredness", 0.2 + random() * 0.2),
                UpdateLevel("fullness", -0.3 - random() * 0.2),
            ]

        return [
            ChangeActivity(Activity.MOVE),
            *self._make_move_action_by_place(human, human.info.liveplace),
            ChangeActivity(Activity.READ),
            Wait(randint(5, 10)),
            UpdateLevel("tiredness", -0.1 - random() * 0.2),
            UpdateLevel("fullness", -0.3 - random() * 0.2),
        ]

    def _make_move_action_by_place(self, human: Human, place_to: Place) -> list[Action]:
        place_from = self.town.find_nearest_place(human.position)
        route = self.town.find_route(place_from, place_to)
        if route is None:
            raise RuntimeError("???")
        return [Move(place) for place in route]

    def _make_move_action_by_function(self, human: Human, func: PF) -> list[Action]:
        place_from = self.town.find_nearest_place(human.position)
        route = None
        while route is None:
            place_to = choice(self.town.places)
            if place_to.function != func:
                continue
            route = self.town.find_route(place_from, place_to)
        return [Move(place) for place in route]
