from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from recomm_town.common import Vec, Trivia
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
    knowledge: list[Trivia]
    actions: list["Action"]
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
        old_position = self.position
        self.position += Vec(dx, dy)
        for cb in self.position_observers:
            cb(self, old_position)

    def teleport(self, x, y):
        old_position = self.position
        self.position = Vec(x, y)
        for cb in self.position_observers:
            cb(self, old_position)
