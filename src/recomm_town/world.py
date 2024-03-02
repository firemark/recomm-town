from collections import defaultdict
from functools import partial
from itertools import chain
from random import choice, randint, random

from recomm_town.common import Trivia, TriviaChunk, Vec
from recomm_town.human import Activity, Emotion, Human
from recomm_town.program import Program
from recomm_town.town import Town, Place, Room, PlaceFunction as PF
from recomm_town.actions import Action
from recomm_town import actions

ENJOY_ACTIVITIES = [Activity.ENJOY_DRINK, Activity.ENJOY_MUSIC, Activity.ENJOY_PLAY]


class World:
    FORGETTING_TICK = 1.0
    FORGETTING_FACTOR = 1.00
    GRID_CELL_SIZE = 100.0
    NEIGHBOR_CELLS = [(x, y) for x in range(-1, 2) for y in range(-1, 2)]

    town: Town
    people: list[Human]
    tracked_human: Human | None
    simulation_speed: float
    people_grid: dict[tuple[int, int], set[Human]]
    radio_program: Program
    tv_program: Program
    forget_lifetime: float

    def __init__(
        self,
        town: Town,
        people: list[Human],
        radio_program: list[Trivia] | None = None,
        tv_program: list[Trivia] | None = None,
    ):
        self.town = town
        self.people = people
        self.simulation_speed = 1.0
        self.people_grid = defaultdict(set)
        self.radio_program = Program(radio_program or [], lifetime=15.0)
        self.tv_program = Program(tv_program or [], lifetime=30.0)
        self.tv_program_index = 0
        self.radio_program_index = 0
        self.forget_lifetime = self.FORGETTING_TICK

        for human in people:
            self._update_human_coords(human, human.position)
            human.position_observers["world"] = self._update_human_coords

    def do_it(self, dt: float):
        dt *= self.simulation_speed
        self.radio_program.do_it(dt)
        self.tv_program.do_it(dt)

        for human in self.people:
            self._do_it_human(human, dt)

        self.forget_lifetime -= dt
        if self.forget_lifetime < 0.0:
            self.forget_lifetime = self.FORGETTING_TICK
            human = choice(self.people)
            self._forget_trivias(human)

    def _update_human_coords(self, human: Human, old_position):
        cell_size = self.GRID_CELL_SIZE
        old_x = int(old_position.x / cell_size)
        old_y = int(old_position.y / cell_size)

        new_x = int(human.position.x / cell_size)
        new_y = int(human.position.y / cell_size)

        if (old_x, old_y) == (new_x, new_y):
            # not changed.
            return

        # remove old position
        for x, y in self.NEIGHBOR_CELLS:
            self.people_grid[old_x + x, old_y + y].discard(human)

        # add new position
        for x, y in self.NEIGHBOR_CELLS:
            self.people_grid[new_x + x, new_y + y].add(human)

    def _find_neighbours(self, human: Human) -> set[Human]:
        cell_size = self.GRID_CELL_SIZE
        new_x = int(human.position.x / cell_size)
        new_y = int(human.position.y / cell_size)
        neighbors = set()
        for x, y in self.NEIGHBOR_CELLS:
            neighbors |= self.people_grid[new_x + x, new_y + y]
        return neighbors - {human}

    def _forget_trivias(self, human: Human):
        forgetting_level = (
            self.FORGETTING_FACTOR * len(human.knowledge) * self.FORGETTING_TICK
        )
        human.forget_trivias(forgetting_level)

    def _do_it_human(self, human: Human, dt: float):
        while not human.actions:
            human.actions = self._make_new_actions(human)

        result = human.actions[0].do_it(human, dt)
        match result:
            case "NEXT":
                action = human.actions.pop(0)
                action.on_destroy(human)
            case "FAIL":
                for action in human.actions:
                    action.on_destroy(human)

                human.actions.clear()

    def _make_new_actions(self, human: Human) -> list[Action]:
        match human.measure_emotion():
            case Emotion.POOR:
                return self._go_to_place(
                    human=human,
                    activity=Activity.WORK,
                    place=human.info.workplace,
                    time=randint(20, 30),
                    talk_probablity=0.5,
                    levels={
                        "money": +0.5 + random() * 0.3,
                        "energy": -0.5 - random() * 0.2,
                        "satiety": -0.5 + random() * 0.3,
                    },
                )
            case Emotion.EMPTY_FRIDGE:
                place = self._find_place_by_function(human, PF.SHOP)
                end_actions: list[Action]
                if place.books and random() > 0.3:
                    end_actions = [actions.BuyBook(choice(place.books))]
                else:
                    end_actions = []
                return self._go_to_place(
                    human=human,
                    activity=Activity.SHOP,
                    place=place,
                    time=randint(5, 10),
                    talk_probablity=0.1,
                    levels={
                        "fridge": 1.0 - random() * 0.2,
                        "money": -0.3 - random() * 0.1,
                        "energy": -0.2 - random() * 0.1,
                        "satiety": -0.1 - random() * 0.1,
                    },
                    end_actions=end_actions,
                )
            case Emotion.HUNGRY:
                return self._go_home(
                    human=human,
                    activity=Activity.EAT,
                    time=randint(5, 10),
                    levels={
                        "fridge": -0.4 - random() * 0.2,
                        "satiety": 1.0 - random() * 0.2,
                        "energy": -0.1 - random() * 0.1,
                    },
                )
            case Emotion.TIRED:
                return self._go_home(
                    human=human,
                    activity=Activity.SLEEP,
                    time=randint(10, 20),
                    levels={
                        "satiety": -0.4 - random() * 0.2,
                        "energy": 1.0,
                    },
                )
            case _:  # otherwise
                possibilities: list[list[Action] | None] = [
                    self._go_fun_fun(human),
                    (
                        None
                        if not human.library
                        else self._go_home_learn(
                            human=human,
                            activity=Activity.READ,
                            trivia=self._choice_chunk(choice(human.library).trivia),
                            learn_level=0.5,
                        )
                    ),
                    (trivia := self.radio_program.trivia)
                    and self._go_home_learn(
                        human=human,
                        activity=Activity.RADIO,
                        trivia=trivia,
                        learn_level=0.05,
                    ),
                    (trivia := self.tv_program.trivia)
                    and self._go_home_learn(
                        human=human,
                        activity=Activity.TV,
                        trivia=trivia,
                        learn_level=0.05,
                    ),
                ]
                filtered_possibilities = [p for p in possibilities if p is not None]
                if not filtered_possibilities:
                    return self._make_fail()
                return choice(filtered_possibilities)

    def _go_fun_fun(self, human: Human) -> list[Action]:
        place = self._find_place_by_function(human, PF.ENTERTAIMENT)
        end_actions: list[Action]
        if place.books and random() > 0.8:
            end_actions = [actions.BuyBook(choice(place.books))]
        else:
            end_actions = []
        return self._go_to_place(
            human=human,
            activity=ENJOY_ACTIVITIES,
            place=place,
            time=randint(5, 10),
            levels={
                "money": -0.1 - random() * 0.2,
                "energy": -0.2 - random() * 0.2,
                "satiety": -0.3 - random() * 0.2,
            },
            end_actions=end_actions,
        )

    def _go_home(
        self,
        human: Human,
        activity: list[Activity] | Activity,
        time: float,
        levels: dict[str, float],
        end_actions: list[Action] | None = None,
    ) -> list[Action]:
        if isinstance(activity, list):
            activity = choice(activity)
        return [
            actions.ChangeActivity(Activity.MOVE),
            *self._make_move_action_to_place(human, human.info.liveplace),
            *self._make_move_action_to_room(human.info.liveroom),
            actions.ChangeActivity(activity),
            actions.UpdateLevelsInTime(time, levels),
            *(end_actions or []),
            actions.ChangeActivity(Activity.MOVE),
            *self._make_move_action_from_room(human.info.liveroom),
        ]

    def _go_home_learn(
        self,
        human: Human,
        activity: Activity,
        trivia: TriviaChunk,
        learn_level: float,
    ) -> list[Action]:
        return self._go_home(
            human=human,
            activity=activity,
            time=randint(5, 10),
            levels={
                "satiety": -0.1 - random() * 0.2,
                "energy": +0.3 + random() * 0.2,
            },
            end_actions=[
                actions.LearnTrivia(trivia, level=learn_level, max_level=1.0),
            ],
        )

    def _go_to_place(
        self,
        human: Human,
        activity: list[Activity] | Activity,
        place: Place,
        time: float,
        levels: dict[str, float],
        end_actions: list[Action] | None = None,
        talk_probablity=0.75,
    ) -> list[Action]:
        if isinstance(activity, list):
            activity = choice(activity)
        end_actions = end_actions or []
        room = self._find_available_room(place)
        if room is None:
            return self._make_fail()
        if random() > 0.5 and place.trivias:
            trivia = choice(place.trivias)
            end_actions.append(
                actions.LearnTrivia(
                    self._choice_trivia(place.trivias),
                    level=0.2,
                    max_level=0.5,
                )
            )

        parts = randint(4, 8)
        ratio = 1 / parts
        find = partial(self._find_neighbours, human)
        main_actions = list(
            chain.from_iterable(
                [
                    actions.UpdateLevelsInTime(time, levels, ratio),
                    actions.RandomTalk(randint(2, 5), find, talk_probablity),
                ]
                for i in range(parts)
            )
        )
        return [
            actions.TakeRoom(room),
            actions.ChangeActivity(Activity.MOVE),
            *self._make_move_action_to_place(human, place),
            *self._make_move_action_to_room(room),
            actions.ChangeActivity(activity),
            *main_actions,
            *(end_actions or []),
            actions.ChangeActivity(Activity.MOVE),
            *self._make_move_action_from_room(room),
            actions.FreeRoom(room),
        ]

    @classmethod
    def _choice_trivia(cls, trivias: list[Trivia]) -> TriviaChunk:
        return cls._choice_chunk(choice(trivias))

    @staticmethod
    def _choice_chunk(trivia: Trivia) -> TriviaChunk:
        return trivia.get_chunk(randint(0, trivia.chunks - 1))

    def _make_fail(self):
        return [actions.ChangeActivity(Activity.WTF), actions.Wait(randint(2, 5))]

    def _make_move_action_to_place(self, human: Human, place_to: Place) -> list[Action]:
        place_from = self.town.find_nearest_place(human.position)
        route = self.town.find_route(place_from, place_to)
        if route is None:
            raise RuntimeError("???")
        acts: list[Action] = []
        for i in range(len(route) - 1):
            place = route[i]
            next_place = route[i + 1]
            way = self.town.path.get((place, next_place))
            if not way:
                acts.append(actions.Move(place.position))

            if place.function == PF.CROSSROAD and random() > 0.9:
                acts += self._wait_at_crossroad(human, place)

            if way:
                acts += [actions.Move(p) for p in way.points]
        return acts

    def _wait_at_crossroad(self, human: Human, place: Place):
        acts: list[Action] = []
        size = place.box_start - place.box_end  # TODO - use rotation argument
        local = Vec(size.x * (random() - 0.5), size.y * (random() - 0.5))
        find = partial(self._find_neighbours, human)
        acts += [
            actions.Move(place.position + local),
            actions.ChangeActivity(Activity.TIME_BREAK),
            actions.Wait(random() * 2.0),
        ]
        for i in range(randint(1, 4)):
            acts += [
                actions.RandomTalk(randint(10, 15) / 10.0, find, probality=0.9),
                actions.Wait(random() * 2.0),
            ]

        acts += [
            actions.ChangeActivity(Activity.MOVE),
            actions.Move(place.position),
        ]
        return acts

    def _make_move_action_to_room(self, room: Room) -> list[Action]:
        act: list[Action] = [actions.Move(vec) for vec in room.path]
        return act + [actions.Move(room.position)]

    def _make_move_action_from_room(self, room: Room) -> list[Action]:
        act: list[Action] = [actions.Move(vec) for vec in room.path[::-1]]
        return [actions.Move(room.position)] + act

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

    def _find_available_room(self, place: Place) -> Room | None:
        available_rooms = [
            room for room in place.rooms if not room.owner and not room.occupied_by
        ]
        return choice(available_rooms) if available_rooms else None
