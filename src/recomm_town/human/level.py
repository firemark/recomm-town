from functools import total_ordering


@total_ordering
class Level:
    value: float

    def __init__(self, value=0.0):
        self.value = max(0.0, min(1.0, value))

    def __repr__(self):
        return f"Level[{self.value:0.3f}]"

    def __eq__(self, other) -> bool:
        if isinstance(other, Level):
            return self.value == other.value
        return self.value == other

    def __lt__(self, other) -> bool:
        if isinstance(other, Level):
            return self.value < other.value
        return self.value < other

    def __add__(self, other) -> "Level":
        if isinstance(other, Level):
            other = other.value
        return Level(self.value + other)

    def __sub__(self, other) -> "Level":
        if isinstance(other, Level):
            other = other.value
        return Level(self.value - other)

    def __mul__(self, other) -> "Level":
        if isinstance(other, Level):
            other = other.value
        return Level(self.value - other)

    def __div__(self, other) -> "Level":
        if isinstance(other, Level):
            other = other.value
        return Level(self.value / other)
