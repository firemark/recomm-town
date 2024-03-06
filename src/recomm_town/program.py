from dataclasses import dataclass
from random import shuffle
from recomm_town.common import Trivia, TriviaChunk


@dataclass
class TriviaWithCounter:
    trivia: Trivia
    counter: int = 0

    def step(self):
        self.counter = (self.counter + 1) % self.trivia.chunks

    def get(self) -> TriviaChunk:
        return self.trivia.get_chunk(self.counter)


class Program:
    trivia: TriviaChunk | None
    _trivias: list[TriviaWithCounter]
    _max_lifetime: float
    _lifetime: float
    _index: int

    def __init__(self, trivias: list[Trivia], lifetime: float, start_after: float):
        self._trivias = [TriviaWithCounter(trivia) for trivia in trivias]
        self._max_lifetime = lifetime
        self._lifetime = lifetime
        self._start_after = start_after
        self._index = 0
        self.time = 0.0

        shuffle(self._trivias)
        if not self._trivias or self._start_after > 0.0:
            self.trivia = None
        else:
            self._change_trivia()

    def do_it(self, dt: float):
        if not self._trivias:
            return
        self.time += dt
        if self.time <= self._start_after:
            return

        self._lifetime -= dt
        if self._lifetime < 0.0:
            self._lifetime = self._max_lifetime
            self._index = (self._index + 1) % len(self._trivias)
            self._change_trivia()

    def _change_trivia(self):
        trivia_with_counter = self._trivias[self._index]
        self.trivia = trivia_with_counter.get()
        trivia_with_counter.step()
