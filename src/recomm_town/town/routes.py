from typing import Optional

from recomm_town.town.place import Place


class Routes:
    __data: dict[tuple[Place, Place], list[Place]]

    def __init__(self) -> None:
        self.__data = {}

    def items(self):
        return self.__data.items()

    def get(self, a: Place, b: Place) -> Optional[list[Place]]:
        if a < b:
            return self.__data.get((a, b))
        else:
            route = self.__data.get((b, a))
            return route and route[::-1]

    def __getitem__(self, __key: tuple[Place, Place]) -> list[Place]:
        a, b = __key
        if a < b:
            return self.__data[a, b]
        else:
            return self.__data[b, a][::-1]

    def __setitem__(self, __key: tuple[Place, Place], __value: list[Place]) -> None:
        a, b = __key
        if a < b:
            self.__data[a, b] = __value
        else:
            self.__data[b, a] = __value[::-1]

    def __len__(self) -> int:
        return len(self.__data)
