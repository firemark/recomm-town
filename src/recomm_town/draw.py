from math import pi
from pyglet.graphics import Batch, Group
from pyglet.shapes import Line, Rectangle, BorderedRectangle, Circle
from pyglet.window import Window
from pyglet.text import Label
from recomm_town.human.activity import Activity

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
    room = _to_color("#3C69E7")
    human = _to_color("#FFCBA4")
    place = _to_color("#EED9C4")
    crossroad = _to_color("#FDD7E4")
    way = _to_color("#AF593E")


LEVELS = ["fridge", "fullness", "money", "tiredness"]
LEVEL_COLORS = {
    "fridge": _to_color("#D9DAD2"),
    "fullness": _to_color("#01A638"),
    "money": _to_color("#F1D651"),
    "tiredness": _to_color("#2D383A"),
}

ACTIVITY_CHAR = {
    Activity.NONE: ("?", _to_color("#000000")),
    Activity.MOVE: ("⚡", _to_color("#E30B5C")),
    Activity.WORK: ("⚒", _to_color("#8B8680")),
    Activity.SHOP: ("$", _to_color("#733380")),
    Activity.TALK: ("!", _to_color("#0095B7")),
    Activity.READ: ("✎", _to_color("#CA3435")),
    Activity.EAT: ("★", _to_color("#CA3435")),
    Activity.SLEEP: ("z", _to_color("#3F26BF")),
    Activity.ENJOY: ("♫", _to_color("#003366")),
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

        act_label = Label("?", x=0, y=size / 4, font_size=36, **kw_font)

        def level_update(attr, value):
            bar = level_bars[attr]
            bar.width = 2 * size * value

        def act_update(activity):
            act_label.text, act_label.color = ACTIVITY_CHAR[activity]

        self.objs += [
            Label(  # Name
                human.info.name,
                x=0,
                y=size * 1.5,
                font_size=14,
                color=_to_color("#E62E6B") + (255,),
                **kw_font,
            ),
            Circle(0, 0, size, color=COLORS.human, **kw),  # Body
            level_bars,
            act_label,
        ]

        human.level_observers.append(level_update)
        human.activity_observers.append(act_update)
