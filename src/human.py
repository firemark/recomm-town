from .common import Vec, Trivia
from .actions import Action


class Human:
    knowledge: list[Trivia]
    actions: list[Action]
    position: Vec
    speed: float

    def __init__(self, position: Vec, speed: float = 2.0):
        self.position = position
        self.knowledge = []
        self.position_observers = []
        self.actions = []
        self.speed = speed

    def move(self, dx, dy):
        self.position = self.position + Vec(dx, dy)
        for cb in self.position_observers:
            cb(self.position)

    def teleport(self, x, y):
        self.position = Vec(x, y)
        for cb in self.position_observers:
            cb(self.position)
