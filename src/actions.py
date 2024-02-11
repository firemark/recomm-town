from typing import Union, Literal, TYPE_CHECKING


if TYPE_CHECKING:
    from .town.place import Place
    from .human import Human


T = Union[Literal["PASS"], Literal["NEXT"], "Action"]


class Action:
    def do_it(self, human: "Human", dt: float) -> T:
        return "PASS"


class Move(Action):
    def __init__(self, place: "Place"):
        self.place = place

    def do_it(self, human: "Human", dt: float) -> T:
        diff = self.place.position - human.position
        if diff.length() < 1.0:
            return "NEXT"

        heading = diff.normalize()
        speed = human.speed
        speed = speed if diff.length() > speed * 2 else 0.5
        vec = heading * speed
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
