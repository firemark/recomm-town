from random import shuffle
from recomm_town.common import Trivia


class Program:
    trivia: Trivia | None
    _trivias: list[Trivia]
    _max_lifetime: float
    _lifetime: float
    _index: int

    def __init__(self, trivias: list[Trivia], lifetime: float):
        self._trivias = trivias.copy()
        self._max_lifetime = lifetime
        self._lifetime = lifetime
        self._index = 0

        shuffle(self._trivias)
        if not self._trivias:
            self.trivia = None
        else:
            self.trivia = self._trivias[self._index]

    def do_it(self, dt: float):
        if not self._trivias:
            return
        self._lifetime -= dt
        if self._lifetime < 0.0:
            self._lifetime = self._max_lifetime
            self._index = (self._index + 1) % len(self._trivias)
            self.trivia = self._trivias[self._index]
