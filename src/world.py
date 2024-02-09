from dataclasses import dataclass

from .human import Human
from .town import Town


@dataclass
class World:
    town: Town
    people: list[Human]
