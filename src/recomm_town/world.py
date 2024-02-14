from random import choice, randint, random

from recomm_town.human import Activity, Emotion, Human
from recomm_town.town.town import Town
from recomm_town.town.place import Place, Room, PlaceFunction as PF
from recomm_town.actions import Action, Move, Wait, ChangeActivity, UpdateLevel, TakeRoom, FreeRoom


class World:
    town: Town
    people: list[Human]
    simulation_speed: float

    def __init__(self, town: Town, people: list[Human]):
        self.town = town
        self.people = people
        self.simulation_speed = 1.0

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
            room = self._find_available_room(human.info.workplace)
            return [
                TakeRoom(room),
                ChangeActivity(Activity.MOVE),
                *self._make_move_action_to_place(human, human.info.workplace),
                *self._make_move_action_to_room(room),
                ChangeActivity(Activity.WORK),
                Wait(randint(20, 30)),
                UpdateLevel("money", 0.5 + random() * 0.3),
                UpdateLevel("tiredness", 0.5 + random() * 0.2),
                UpdateLevel("fullness", -0.5 + random() * 0.3),
                *self._make_move_action_from_room(room),
                FreeRoom(room),
            ]
        if emotion == Emotion.EMPTY_FRIDGE:
            shop = self._find_place_by_function(human, PF.SHOP)
            room = self._find_available_room(shop)
            return [
                TakeRoom(room),
                ChangeActivity(Activity.MOVE),
                *self._make_move_action_to_place(human, shop),
                *self._make_move_action_to_room(room),
                ChangeActivity(Activity.SHOP),
                Wait(randint(5, 10)),
                UpdateLevel("fridge", 1.0 - random() * 0.2),
                UpdateLevel("money", -0.3 - random() * 0.1),
                UpdateLevel("tiredness", 0.2 + random() * 0.1),
                UpdateLevel("fullness", -0.1 - random() * 0.1),
                *self._make_move_action_from_room(room),
                FreeRoom(room),
            ]
        if emotion == Emotion.HUNGRY:
            return [
                ChangeActivity(Activity.MOVE),
                *self._make_move_action_to_place(human, human.info.liveplace),
                *self._make_move_action_to_room(human.info.liveroom),
                ChangeActivity(Activity.EAT),
                Wait(randint(5, 10)),
                UpdateLevel("fridge", -0.4 - random() * 0.2),
                UpdateLevel("fullness", 1.0 - random() * 0.2),
                UpdateLevel("tiredness", 0.1 + random() * 0.1),
                *self._make_move_action_from_room(human.info.liveroom),
            ]
        if emotion == Emotion.TIRED:
            return [
                ChangeActivity(Activity.MOVE),
                *self._make_move_action_to_place(human, human.info.liveplace),
                *self._make_move_action_to_room(human.info.liveroom),
                ChangeActivity(Activity.SLEEP),
                Wait(randint(10, 20)),
                UpdateLevel("tiredness", -1.0),
                UpdateLevel("fullness", -0.4 - random() * 0.2),
                *self._make_move_action_from_room(human.info.liveroom),
            ]

        r = random()

        if r > 0.5:
            place = self._find_place_by_function(human, PF.ENTERTAIMENT)
            room = self._find_available_room(place)
            return [
                TakeRoom(room),
                ChangeActivity(Activity.MOVE),
                *self._make_move_action_to_place(human, place),
                *self._make_move_action_to_room(room),
                ChangeActivity(Activity.ENJOY),
                Wait(randint(5, 10)),
                UpdateLevel("money", -0.1 - random() * 0.2),
                UpdateLevel("tiredness", 0.2 + random() * 0.2),
                UpdateLevel("fullness", -0.3 - random() * 0.2),
                *self._make_move_action_from_room(room),
                FreeRoom(room),
            ]

        return [
            ChangeActivity(Activity.MOVE),
            *self._make_move_action_to_place(human, human.info.liveplace),
            *self._make_move_action_to_room(human.info.liveroom),
            ChangeActivity(Activity.READ),
            Wait(randint(5, 10)),
            UpdateLevel("tiredness", -0.1 - random() * 0.2),
            UpdateLevel("fullness", -0.3 - random() * 0.2),
            *self._make_move_action_from_room(human.info.liveroom),
        ]

    def _make_move_action_to_place(self, human: Human, place_to: Place) -> list[Action]:
        place_from = self.town.find_nearest_place(human.position)
        route = self.town.find_route(place_from, place_to)
        if route is None:
            raise RuntimeError("???")
        return [Move(place.position) for place in route]

    def _make_move_action_to_room(self, room: Room) -> list[Action]:
        actions: list[Action] =  [Move(vec) for vec in room.path]
        return actions + [Move(room.position)]

    def _make_move_action_from_room(self, room: Room) -> list[Action]:
        actions: list[Action] =  [Move(vec) for vec in room.path[::-1]]
        return [Move(room.position)] + actions

    def _find_place_by_function(self, human: Human, func: PF) -> Place:
        place_from = self.town.find_nearest_place(human.position)
        while True:
            place_to = choice(self.town.places)
            if place_to.function != func:
                continue
            route = self.town.find_route(place_from, place_to)
            if route is None:
                continue
            break
        return place_to

    def _find_available_room(self, place: Place) -> Room:
        available_rooms = [room for room in place.rooms if not room.owner and not room.occupied_by]
        if not available_rooms:
            print("NO ROOMS!", place)
        return choice(available_rooms)