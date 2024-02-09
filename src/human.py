from .common import Vec, Trivia
from .actions import Action


class Human:
    knowledge: list[Trivia]
    actions: list[Action]
    position: Vec

    def __init__(self, position: Vec):
        self.position = position
        self.knowledge = []
        self.position_observers = []
        self.actions = []

    def move(self, dx, dy):
        self.position = self.position + Vec(dx, dy)
        for cb in self.position_observers:
            cb(self.position)
