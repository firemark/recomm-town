from collections import defaultdict

from pyglet.graphics import Batch, Group
from pyglet.sprite import Sprite
from pyglet.image import ImageGrid, load as image_load
from pyglet.shapes import Line, Rectangle, BorderedRectangle, Circle
from pyglet.window import Window
from pyglet.text import Label

from recomm_town.app import GuiGroup
from recomm_town.human import Human, Activity
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

ACTIVITY_COLORS = {
    Activity.NONE: _to_color("#000000"),
    Activity.MOVE: _to_color("#E30B5C"),
    Activity.WORK: _to_color("#8B8680"),
    Activity.SHOP: _to_color("#A63A79"),
    Activity.TALK: _to_color("#FFFFFF"),
    Activity.READ: _to_color("#CA3435"),
    Activity.EAT: _to_color("#CA3435"),
    Activity.SLEEP: _to_color("#0066CC"),
    Activity.ENJOY_DRINK: _to_color("#02A4D3"),
    Activity.ENJOY_PLAY: _to_color("#02A4D3"),
    Activity.ENJOY_MUSIC: _to_color("#02A4D3"),
    Activity.SHARE_LOVE: _to_color("#FE6F5E"),
    Activity.SHARE_MUSIC: _to_color("#FE6F5E"),
    Activity.SHARE_WOW: _to_color("#FE6F5E"),
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
        self.trivias_level = defaultdict(float)
        self.activity_sprites = ImageGrid(image_load("textures/activities.png"), 4, 4)

    def draw_gui(self, people_count, group: GuiGroup):
        kw = dict(**self.kw, group=group)
        self.people_count = people_count
        self.trivia_dashboard = Label(
            text="",
            font_name="Monospace",
            font_size=16,
            multiline=True,
            color=(0, 0, 0, 255),
            width=700.0,
            anchor_x="left",
            anchor_y="top",
            bold=True,
            x=50.0,
            y=-20.0,
            **kw,
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
            human.position_observers["draw"] = group.update
            self._draw_human(human, group)

    def _draw_human(self, human: Human, group: HumanGroup):
        size = 20
        kw = dict(**self.kw, group=group)
        kw_font = dict(
            **self.kw_font,
            bold=True,
            group=group,
        )

        level_bars = {
            level: BorderedRectangle(
                -size,
                -size * 1.6 - size / 2 * (4 - index),
                2 * size * getattr(human.levels, level).value,
                size / 2,
                color=LEVEL_COLORS[level],
                border=5,
                **kw,
            )
            for index, level in enumerate(LEVELS, start=1)
        }

        act_sprite = Sprite(img=self.activity_sprites[0], **kw)
        act_sprite.update(x=-size, y=-size, scale=size / 98)

        def level_update(attr, value):
            bar = level_bars[attr]
            bar.width = 2 * size * value

        def act_update(activity):
            act_sprite.image = self.activity_sprites[activity]
            act_sprite.color = ACTIVITY_COLORS[activity]

        def trivia_update(trivia, new, old):
            diff = new - old
            if diff == 0.0:
                return
            self.trivias_level[trivia] += diff
            c = self.people_count
            gen = enumerate(
                sorted(self.trivias_level.items(), key=lambda o: -o[1]), start=1
            )
            self.trivia_dashboard.text = "\n".join(
                f"{i:2}. {f'[{t.category}] {t.name}':30} {l / c  * 100:6.2f}%"
                for i, (t, l) in gen
            )

        self.objs += [
            Label(  # Name
                human.info.name,
                x=0,
                y=size * 2.5,
                font_size=14,
                color=_to_color("#2D383A") + (255,),
                **kw_font,
            ),
            Circle(0, 0, size, color=COLORS.human, **kw),  # Body
            level_bars,
            act_sprite,
        ]

        human.level_observers["draw"] = level_update
        human.activity_observers["draw"] = act_update
        human.knowledge_observers["draw"] = trivia_update
