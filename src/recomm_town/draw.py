from math import pi
from pyglet.graphics import Batch, Group
from pyglet.shapes import Line, Rectangle, BorderedRectangle, Circle
from pyglet.window import Window
from pyglet.text import Label

from recomm_town.human.human import Human
from recomm_town.town import PlaceFunction as PF
from recomm_town.town.place import Place, Way


def _to_color(x: str) -> tuple[int, int, int]:
    assert x[0] == "#"
    r = int(x[1:3], 16)
    g = int(x[3:5], 16)
    b = int(x[5:7], 16)
    return (r, g, b)


class COLORS:
    room = (0x00, 0x00, 0xFF)
    human = (0xFF, 0xFF, 0xFF)
    place = (0xAA, 0xAA, 0xAA)
    crossroad = (0x00, 0xFF, 0x00)
    way = (0xFF, 0x00, 0x00)


LEVELS = ["fridge", "fullness", "money", "tiredness"]
LEVEL_COLORS = {
    "fridge": _to_color("#D9DAD2"),
    "fullness": _to_color("#F1D651"),
    "money": _to_color("#01A638"),
    "tiredness": _to_color("#2D383A"),
}


class HumanGroup(Group):
    x: float
    y: float

    def __init__(self, window: Window, index: int, human: Human, parent: Group):
        super().__init__(index, parent)
        self._window = window
        self.x = human.position.x
        self.y = human.position.y

    def update(self, human: Human, _):
        self.x = human.position.x
        self.y = human.position.y

    def set_state(self):
        self._old_view = self._window.view
        self._window.view = self._window.view.translate((self.x, self.y, 0.0))

    def unset_state(self):
        self._window.view = self._old_view


class Draw:
    def __init__(self, batch: Batch) -> None:
        self.objs = []
        self.kw = dict(batch=batch)
        self.kw_font = dict(
            font_name="Monospace",
            anchor_x="center",
            anchor_y="center",
            **self.kw,
        )

    def draw_path(self, path: list[Way], group: Group):
        kw = dict(**self.kw, group=group, width=50.0, color=COLORS.way)
        for way in path:
            a = way.a.position
            b = way.b.position
            self.objs.append(Line(a.x, a.y, b.x, b.y, **kw))

    def draw_places(self, places: list[Place], group: Group):
        kw = dict(**self.kw, group=group)
        kw_font = dict(**self.kw_font, color=(0, 0, 0, 255), font_size=36, group=group)

        for place in places:
            color = COLORS.crossroad if place.function == PF.CROSSROAD else COLORS.place
            p = place.position
            start = place.box_start
            size = place.box_end - start

            self.objs += [
                Rectangle(start.x, start.y, size.x, size.y, color=color, **kw),
                Label(place.name, x=p.x, y=p.y, **kw_font),
            ]

            s = place.room_size
            h = s / 2
            for room in place.rooms:
                r = room.position - h
                self.objs.append(Rectangle(r.x, r.y, s, s, color=COLORS.room, **kw))

    def draw_people(self, window: Window, people: list[Human], people_group: Group):
        for index, human in enumerate(people):
            group = HumanGroup(window, index, human, people_group)
            human.position_observers.append(group.update)
            self._draw_human(human, group)

    def _draw_human(self, human: Human, group: HumanGroup):
        size = 20
        kw = dict(**self.kw, group=group)
        kw_font = dict(
            **self.kw_font,
            color=(0x00, 0x11, 0x44, 255),
            font_size=14,
            bold=True,
            group=group,
        )

        level_bars = {}
        for index, level in enumerate(LEVELS, start=1):
            bar = BorderedRectangle(
                -size,
                -size * 1.6 - size / 2 * (4 - index),
                2 * size * getattr(human.levels, level).value,
                size / 2,
                color=LEVEL_COLORS[level],
                border=5,
                **kw,
            )
            level_bars[level] = bar

        self.objs += [
            Label(human.info.name, x=0, y=size * 1.5, **kw_font),  # Name
            Circle(0, 0, size, color=COLORS.human, **kw),  # Body
            level_bars,
        ]

        def update(attr, value):
            bar = level_bars[attr]
            bar.width = 2 * size * value

        human.level_observers.append(update)
