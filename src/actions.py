from typing import Union, Literal, TYPE_CHECKING


if TYPE_CHECKING:
    from .town import Place


T = Union[Literal["PASS"], Literal["NEXT"], "Action"]


class Action:
    def do_it(self, human: "Human") -> T:
        return "PASS"


class Move(Action):
    def __init__(self, place: "Place", speed=2.0):
        self.place = place
        self.speed = speed

    def do_it(self, human: "Human") -> T:
        diff = self.place.position - human.position
        if diff.length() < 1.0:
            return "NEXT"

        heading = diff.normalize()
        vec = heading * self.speed
        human.move(vec.x, vec.y)
        return "PASS"
