from functools import partial
from typing import Callable, Literal
from random import choice, randint, random

from recomm_town.common import Book, TriviaChunk, Vec
from recomm_town.town.place import Room
from recomm_town.human import Human, Activity


T = Literal["FAIL", "PASS", "STOP", "NEXT"]
SHARE_ACTIVITIES = [Activity.SHARE_LOVE, Activity.SHARE_MUSIC, Activity.SHARE_WOW]


class Action:
    def do_it(self, human: "Human", dt: float) -> T:
        return "PASS"


class ActionWithStart(Action):
    __first_time: bool = True

    def do_it(self, human: "Human", dt: float) -> T:
        if self.__first_time:
            self.__first_time = False
            result = self.on_start(human)
            if result != "PASS":
                return result
        return self.on_invoke(human, dt)

    def on_start(self, human: "Human") -> T:
        return "PASS"

    def on_invoke(self, human: "Human", dt: float) -> T:
        return "PASS"


class Move(Action):
    def __init__(self, position: Vec):
        self.position = position

    def do_it(self, human: "Human", dt: float) -> T:
        diff = self.position - human.position
        speed = human.info.speed * (dt * 60.0)
        if diff.length() < speed * 2:
            human.teleport(self.position.x, self.position.y)
            return "NEXT"

        vec = diff.normalize() * speed
        human.move(vec.x, vec.y)
        return "PASS"


class UpdateLevelsInTime(Action):
    def __init__(
        self,
        time: float,
        levels: dict[str, float],
        ratio: float = 1.0,
    ):
        self.total_time = ratio * time
        self.time = ratio * time
        self.levels = levels
        self.ratio = ratio

    def do_it(self, human: "Human", dt: float) -> T:
        self.time -= dt
        if self.time <= 0.0:
            return "NEXT"
        ratio = self.ratio * dt / self.total_time
        for attr, value in self.levels.items():
            human.update_level(attr, value * ratio)
        return "PASS"


class LearnTrivia(Action):
    def __init__(self, trivia: TriviaChunk, level: float, max_level: float):
        self.trivia = trivia
        self.level = level
        self.max_level = max_level

    def do_it(self, human: "Human", dt: float) -> T:
        human.update_knowledge(self.trivia, self.level, max_value=self.max_level)
        return "NEXT"


class BuyBook(Action):
    def __init__(self, book: Book):
        self.book = book

    def do_it(self, human: "Human", dt: float) -> T:
        if self.book not in human.library:
            human.library.append(self.book)
        return "NEXT"


class ChangeActivity(Action):
    def __init__(self, activity: "Activity") -> None:
        self.activity = activity

    def do_it(self, human: "Human", dt: float) -> T:
        # name = human.info.name
        # print(name)
        # print("    changes activity", human.activity.name, "=>", self.activity.name)
        # print("    emotion:", human.measure_emotion().name)
        # print("    levels:", human.levels)
        human.update_activity(self.activity)
        return "NEXT"


class RandomTalk(ActionWithStart):
    def __init__(
        self,
        time: float,
        find_neighbours: Callable[[], list[Human]],
        probality: float = 0.75,
    ) -> None:
        self.time = time
        self.find_neighbours = find_neighbours
        self.probality = probality

    def on_start(self, human: Human) -> T:
        if random() >= self.probality:
            return "NEXT"
        for stranger in self.find_neighbours():
            if stranger.activity != Activity.TALK:
                continue

            self_trust = human.get_trust_level(stranger)
            stranger_trust = stranger.get_trust_level(human)
            trust = (self_trust + stranger_trust) / 2.0
            if random() < trust:
                continue

            if stranger.knowledge and human.knowledge:
                if random() > 0.5:
                    return self._share(stranger, human)
                else:
                    return self._share(human, stranger)
            if stranger.knowledge:
                return self._share(stranger, human)
            elif human.knowledge:
                return self._share(human, stranger)

        self.previous_activity = human.activity
        human.update_activity(Activity.TALK)
        return "PASS"

    @staticmethod
    def _share(teacher: Human, student: Human):
        trivia = choice(list(teacher.knowledge.keys()))
        chunk_id = choice(list(teacher.knowledge[trivia].keys()))
        trivia_chunk = trivia.get_chunk(chunk_id)

        time_to_share = randint(2, 5)
        teacher.actions[0] = ShareTo(time_to_share, trivia_chunk, student)
        student.actions[0] = ShareFrom(time_to_share, trivia_chunk, teacher)
        teacher.start_talk(student, trivia)
        return "STOP"

    def on_invoke(self, human: "Human", dt: float) -> T:
        self.time -= dt
        if self.time <= 0.0:
            human.update_activity(self.previous_activity)
            return "NEXT"
        return "PASS"


class Share(ActionWithStart):
    def __init__(
        self,
        time: float,
        other: Human,
        trivia: TriviaChunk,
        level: float = 0.2,
        max: float = 1.0,
    ) -> None:
        self.time = time
        self.other = other
        self.trivia = trivia
        self.level = level
        self.max = max

    def on_start(self, human: Human) -> T:
        self.previous_activity = human.activity
        human.update_activity(choice(SHARE_ACTIVITIES))
        return "PASS"

    def on_stop(self, human: Human):
        human.update_activity(self.previous_activity)
        human.update_knowledge(self.trivia, self.level, self.max)
        human.update_friend_level(self.other, random() * 0.2)

    def on_invoke(self, human: Human, dt: float) -> T:
        self.time -= dt
        if self.time <= 0.0:
            self.on_stop(human)
            return "NEXT"

        return "PASS"


class ShareFrom(Share):

    def __init__(self, time: float, trivia: TriviaChunk, teacher: Human):
        teach_level = randint(2, 5) / 10
        teacher_level = teacher.knowledge[trivia.trivia][trivia.id]
        super().__init__(time, teacher, trivia, level=teach_level, max=teacher_level)


class ShareTo(Share):

    def __init__(self, time: float, trivia: TriviaChunk, student: Human):
        super().__init__(time, student, trivia, level=0.2, max=1.0)
        self.student = student

    def on_stop(self, human: Human):
        super().on_stop(human)
        human.stop_talk(self.student)


class Wait(Action):
    def __init__(self, time) -> None:
        self.time = time

    def do_it(self, human: "Human", dt: float) -> T:
        self.time -= dt
        if self.time <= 0.0:
            return "NEXT"

        return "PASS"


class TakeRoom(Action):
    def __init__(self, room: Room) -> None:
        self.room = room

    def do_it(self, human: "Human", dt: float) -> T:
        self.room.occupied_by = human
        return "NEXT"


class FreeRoom(Action):
    def __init__(self, room: Room) -> None:
        self.room = room

    def do_it(self, human: "Human", dt: float) -> T:
        self.room.occupied_by = None
        return "NEXT"
