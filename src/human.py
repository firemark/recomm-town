from .common import Vec, Trivia


class Human:
    knowledge: list[Trivia]
    position: Vec

    def __init__(self, position: Vec):
        self.position = position
        self.knowledge = []
