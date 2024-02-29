from typing import Callable


class Observer[*Args](dict[str, Callable[[*Args], None]]):

    def __call__(self, *args: *Args) -> None:
        for callback in self.values():
            callback(*args)
