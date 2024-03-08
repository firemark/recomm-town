from itertools import chain
from math import ceil, cos, degrees, radians, sin
from recomm_town.common import Vec
from recomm_town.town.place import LocalRoom


class RoomFactories:

    @staticmethod
    def flat(n, m):
        max_lvl = m * 2 - 4

        for y in range(-1, m * 2 - 1, 2):
            lvl = min(max_lvl, y + 1)
            yield from (
                LocalRoom(Vec(-x, +y), [Vec(0, lvl), Vec(-x, lvl)])
                for x in chain.from_iterable((-x, x) for x in range(+1, n + 1))
            )

    @staticmethod
    def grid(n):
        return (
            LocalRoom(Vec(x, y), [Vec(x + hall, 0), Vec(x + hall, y)])
            for x, y, hall in chain.from_iterable(
                [(-x, -y, +0.5), (-x, +y, +0.5), (+x, +y, -0.5), (+x, -y, -0.5)]
                for x in range(1, n + 1)
                for y in range(1, n + 1)
            )
        )

    @staticmethod
    def __rvec(radius: float, angle: float) -> Vec:
        return Vec(sin(angle), cos(angle)) * radius

    @classmethod
    def round(cls, rows: int, in_rows: int):
        rvec = cls.__rvec
        radius = 0.5 * rows

        for part in range(4):
            langle_shift = radians(90) * part
            rangle_shift = langle_shift + radians(90)
            for row in range(1, rows + 1):
                prerow_radius = row * radius + 0.5
                row_radius = prerow_radius + 0.5
                in_rows_part = (in_rows + 1) * ceil(row / 1.5)
                angle = radians(90) / in_rows_part

                lsteps = [rvec(prerow_radius, langle_shift)]
                rsteps = [rvec(prerow_radius, rangle_shift)]
                lside = in_rows_part // 2
                rside = in_rows_part - lside + 1
                for i in range(1, lside):
                    a = langle_shift + angle * i
                    position = rvec(row_radius, a)
                    lsteps.append(rvec(prerow_radius, a))
                    yield LocalRoom(position, lsteps.copy(), rotation=degrees(a))
                for i in range(1, rside):
                    a = rangle_shift - angle * i
                    position = rvec(row_radius, a)
                    rsteps.append(rvec(prerow_radius, a))
                    yield LocalRoom(position, rsteps.copy(), rotation=degrees(a))
