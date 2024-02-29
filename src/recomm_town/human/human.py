from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

from recomm_town.common import Book, Vec, Trivia, TriviaChunk
from recomm_town.human.level import Level
from recomm_town.human.activity import Activity
from recomm_town.human.emotion import Emotion
from recomm_town.observer import Observer


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
    stranger_trust_level: float = 0.5


@dataclass
class Levels:
    fridge: Level = field(default_factory=lambda: Level(1.0))
    fullness: Level = field(default_factory=lambda: Level(1.0))
    money: Level = field(default_factory=lambda: Level(0.0))
    tiredness: Level = field(default_factory=lambda: Level(0.0))


class Human:
    knowledge: dict[Trivia, dict[int, float]]
    actions: list["Action"]
    library: list[Book]
    position: Vec
    info: HumanInfo
    levels: Levels
    activity: Activity
    friend_levels: defaultdict["Human", Level]

    def __init__(self, position: Vec, info: HumanInfo):
        self.position = position
        self.knowledge = {}
        self.friend_levels = defaultdict(Level)
        self.actions = []
        self.library = []
        self.info = info
        self.levels = Levels()
        self.activity = Activity.NONE

        self.position_observers: Observer["Human", Vec] = Observer()
        self.level_observers: Observer[str, float] = Observer()
        self.activity_observers: Observer[Activity] = Observer()
        self.knowledge_observers: Observer[TriviaChunk, float, float] = Observer()
        self.talk_observers: Observer["Human", "Human", Trivia | None, str] = Observer()
        self.friend_observers: Observer["Human", "Human", float] = Observer()

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

    def get_trust_level(self, other: "Human") -> float:
        return self.friend_levels[other].value + self.info.stranger_trust_level

    def replace_first_action(self, action: "Action"):
        if self.actions:
            self.actions[0].on_destroy(self)
            self.actions[0] = action
        else:
            self.actions.append(action)

    def start_talk(self, stranger: Self, trivia: Trivia):
        self.talk_observers(self, stranger, trivia, "START")

    def stop_talk(self, stranger: Self):
        self.talk_observers(self, stranger, None, "STOP")

    def update_activity(self, activity: Activity):
        self.activity = activity
        self.activity_observers(activity)

    def update_level(self, attr: str, value: float):
        level = getattr(self.levels, attr)
        level += value
        setattr(self.levels, attr, level)
        self.level_observers(attr, level.value)

    def update_friend_level(self, other: "Human", value: float = 0.1):
        if other is self:
            return
        self.friend_levels[other] += value
        if value < 0.0:
            return
        count = sum(2 for l in self.friend_levels.values() if l > 0.0)
        if count == 0:
            return
        dec_value = value / count
        for friend in self.friend_levels.keys():
            if other is friend:
                continue
            self.friend_levels[friend] -= dec_value
        self.friend_observers(self, other, self.friend_levels[other].value)

    def update_knowledge(
        self, trivia_chunk: TriviaChunk, value: float, max_value: float = 1.0
    ):
        trivia, chunk_id = trivia_chunk
        try:
            chunks = self.knowledge[trivia]
        except KeyError:
            chunks = {}
            self.knowledge[trivia] = chunks

        prev_value = chunks.get(chunk_id, 0.0)
        new_value = prev_value + min(value, max(0.0, max_value - prev_value))
        chunks[chunk_id] = new_value
        self.knowledge_observers(trivia_chunk, new_value, prev_value)

    def forget_trivias(self, forgetting_factor: float):
        if not self.knowledge:
            return
        new_knowledge: dict[Trivia, dict[int, float]] = {}
        for trivia, chunks in self.knowledge.items():
            forgetting_level = (
                trivia.forgetting_level * forgetting_factor / trivia.chunks
            )
            new_chunks: dict[int, float] = {}
            for chunk_id, level in chunks.items():
                new_level = max(0.0, level - forgetting_level)
                new_chunks[chunk_id] = new_level
                self.knowledge_observers(trivia.get_chunk(chunk_id), new_level, level)
            new_knowledge[trivia] = new_chunks
        self.knowledge = new_knowledge

    def move(self, dx, dy):
        old_position = self.position
        self.position += Vec(dx, dy)
        self.position_observers(self, old_position)

    def teleport(self, x, y):
        old_position = self.position
        self.position = Vec(x, y)
        self.position_observers(self, old_position)
