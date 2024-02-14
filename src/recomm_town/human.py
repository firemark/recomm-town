from dataclasses import dataclass, field
from functools import total_ordering
from enum import Enum, auto
from typing import TYPE_CHECKING

from recomm_town.common import Vec, Trivia
from recomm_town.actions import Action


if TYPE_CHECKING:
    from recomm_town.town.place import Place, Room


class Activity(Enum):
    NONE = auto()
    MOVE = auto()
    WORK = auto()
    SHOP = auto()
    TALK = auto()
    READ = auto()
    EAT = auto()
    SLEEP = auto()
    ENJOY = auto()


class Emotion(Enum):
    HAPPY = auto()
    EMPTY_FRIDGE = auto()
    HUNGRY = auto()
    SAD = auto()
    POOR = auto()
    TIRED = auto()


@dataclass
class HumanInfo:
    name: str
    liveplace: "Place"
    liveroom: "Room"
    workplace: "Place"
    speed: float = 5.0


@total_ordering
class Level:
    value: float

    def __init__(self, value=0.0):
        self.value = max(0.0, min(1.0, value))

    def __repr__(self):
        return f"Level[{self.value:0.3f}]"

    def __eq__(self, other) -> bool:
        if isinstance(other, Level):
            return self.value == other.value
        return self.value == other

    def __lt__(self, other) -> bool:
        if isinstance(other, Level):
            return self.value < other.value
        return self.value < other

    def __add__(self, other) -> "Level":
        if isinstance(other, Level):
            other = other.value
        return Level(self.value + other)

    def __sub__(self, other) -> "Level":
        if isinstance(other, Level):
            other = other.value
        return Level(self.value - other)

    def __mul__(self, other) -> "Level":
        if isinstance(other, Level):
            other = other.value
        return Level(self.value - other)

    def __div__(self, other) -> "Level":
        if isinstance(other, Level):
            other = other.value
        return Level(self.value / other)


@dataclass
class Levels:
    fridge: Level = field(default_factory=lambda: Level(1.0))
    fullness: Level = field(default_factory=lambda: Level(1.0))
    money: Level = field(default_factory=lambda: Level(0.0))
    tiredness: Level = field(default_factory=lambda: Level(0.0))


class Human:
    knowledge: list[Trivia]
    actions: list[Action]
    position: Vec
    info: HumanInfo
    levels: Levels
    activity: Activity

    def __init__(self, position: Vec, info: HumanInfo):
        self.position = position
        self.knowledge = []
        self.position_observers = []
        self.actions = []
        self.info = info
        self.levels = Levels()
        self.activity = Activity.NONE

    def measure_emotion(self) -> Emotion:
        levels = self.levels
        if levels.money < 0.5:
            return Emotion.POOR
        if levels.fullness < 0.5:
            if levels.fridge < 0.4:
                return Emotion.EMPTY_FRIDGE
            else:
                return Emotion.HUNGRY
        if levels.tiredness > 0.6:
            return Emotion.TIRED

        return Emotion.HAPPY

    def move(self, dx, dy):
        self.position = self.position + Vec(dx, dy)
        for cb in self.position_observers:
            cb(self.position)

    def teleport(self, x, y):
        self.position = Vec(x, y)
        for cb in self.position_observers:
            cb(self.position)
