from typing import Literal
from random import random

from recomm_town.common import Vec
from recomm_town.town.place import Room
from recomm_town.human import Human, Activity


T = Literal["FAIL", "PASS", "NEXT"] | list["Action"]


class Action:
    def on_start(self, human: "Human") -> T:
        return "PASS"

    def do_it(self, human: "Human", dt: float) -> T:
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


class Wait(Action):
    def __init__(self, time: float):
        self.time = time

    def do_it(self, human: "Human", dt: float) -> T:
        self.time -= dt
        if self.time <= 0.0:
            return "NEXT"
        return "PASS"


class UpdateLevelsInTime(Action):
    def __init__(self, time: float, levels: dict[str, float], ratio: float = 1.0):
        self.total_time = ratio * time
        self.time = ratio * time
        self.levels = levels
        self.ratio = ratio

    def do_it(self, human: "Human", dt: float) -> T:
        self.time -= dt
        if self.time <= 0.0:
            ratio = self.ratio * (dt - self.time) / self.total_time
            for attr, value in self.levels.items():
                human.update_level(attr, value * ratio)
            return "NEXT"
        ratio = self.ratio * dt / self.total_time
        for attr, value in self.levels.items():
            human.update_level(attr, value * ratio)
        return "PASS"


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

class RandomTalk(Action):
    def __init__(self, time: float) -> None:
        self.time = time

    def on_start(self, human: Human) -> T:
        if random() > 0.5:
            return "NEXT"
        self.previous_activity = human.activity
        human.update_activity(Activity.TALK)
        return "PASS"

    def do_it(self, human: "Human", dt: float) -> T:
        self.time -= dt
        if self.time <= 0.0:
            human.update_activity(self.previous_activity)
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
