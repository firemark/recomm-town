from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

from recomm_town.common import Book, Vec, Trivia
from recomm_town.human.level import Level
from recomm_town.human.activity import Activity
from recomm_town.human.emotion import Emotion


if TYPE_CHECKING:
    from recomm_town.actions import Action
    from recomm_town.town import Place, Room


@dataclass
class HumanInfo:
    name: str
    liveplace: "Place"
    liveroom: "Room"
    workplace: "Place"
    speed: float = 5.0


@dataclass
class Levels:
    fridge: Level = field(default_factory=lambda: Level(1.0))
    fullness: Level = field(default_factory=lambda: Level(1.0))
    money: Level = field(default_factory=lambda: Level(0.0))
    tiredness: Level = field(default_factory=lambda: Level(0.0))


class Human:
    knowledge: dict[Trivia, float]
    actions: list["Action"]
    library: list[Book]
    position: Vec
    info: HumanInfo
    levels: Levels
    activity: Activity

    def __init__(self, position: Vec, info: HumanInfo):
        self.position = position
        self.knowledge = defaultdict(float)
        self.position_observers = {}
        self.level_observers = {}
        self.activity_observers = {}
        self.knowledge_observers = {}
        self.talk_observers = {}
        self.actions = []
        self.library = []
        self.info = info
        self.levels = Levels()
        self.activity = Activity.NONE

    def measure_emotion(self) -> Emotion:
        levels = self.levels
        if levels.money < 0.5:
            return Emotion.POOR
        if levels.fridge < 0.4:
            return Emotion.EMPTY_FRIDGE
        if levels.fullness < 0.5:
            return Emotion.HUNGRY
        if levels.tiredness > 0.6:
            return Emotion.TIRED

        return Emotion.HAPPY

    def start_talk(self, stranger: Self, trivia: Trivia):
        for cb in self.talk_observers.values():
            cb(self, stranger, trivia, "START")

    def stop_talk(self, stranger: Self):
        for cb in self.talk_observers.values():
            cb(self, stranger, None, "STOP")

    def update_activity(self, activity: Activity):
        self.activity = activity
        for cb in self.activity_observers.values():
            cb(activity)

    def update_level(self, attr: str, value: float):
        level = getattr(self.levels, attr)
        level += value
        setattr(self.levels, attr, level)
        for cb in self.level_observers.values():
            cb(attr, level.value)

    def update_knowledge(self, trivia: Trivia, value: float, max_value: float = 1.0):
        prev_value = self.knowledge[trivia]
        new_value = prev_value + min(value, max(0.0, max_value - prev_value))
        self.knowledge[trivia] = new_value
        for cb in self.knowledge_observers.values():
            cb(trivia, new_value, prev_value)

    def move(self, dx, dy):
        old_position = self.position
        self.position += Vec(dx, dy)
        for cb in self.position_observers.values():
            cb(self, old_position)

    def teleport(self, x, y):
        old_position = self.position
        self.position = Vec(x, y)
        for cb in self.position_observers.values():
            cb(self, old_position)
