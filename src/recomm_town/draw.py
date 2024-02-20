from collections import defaultdict
from random import randint, random

from pyglet.graphics import Batch, Group
from pyglet.image import ImageGrid, load as image_load
from pyglet.shapes import Line, Rectangle, BorderedRectangle
from pyglet.window import Window
from pyglet.text import Label

from recomm_town.app import GuiGroup
from recomm_town.shaders import AnimatedLine, Sprite
from recomm_town.common import Color, Trivia, Vec
from recomm_town.human import Human, Activity
from recomm_town.town import PlaceFunction as PF
from recomm_town.town.place import Place, Way


def _to_color(x: str) -> tuple[int, int, int]:
    assert x[0] == "#"
    r = int(x[1:3], 16)
    g = int(x[3:5], 16)
    b = int(x[5:7], 16)
    return (r, g, b)


def _c(x: str) -> tuple[int, int, int, int]:
    assert x[0] == "#"
    r = int(x[1:3], 16)
    g = int(x[3:5], 16)
    b = int(x[5:7], 16)
    a = int(x[7:9] or "FF", 16)
    return (r, g, b, a)


def _n():
    return (0, 0, 0, 0)


class COLORS:
    room_a = Color.from_hex("#50BFE6")
    room_b = Color.from_hex("#01A638")
    place_a = Color.from_hex("#EED9C4")
    place_b = Color.from_hex("#C0D5F0")
    crossroad_a = Color.from_hex("#FDD7E4")
    crossroad_b = Color.from_hex("#FEBAAD")
    way_a = Color.from_hex("#AF593E")
    way_b = Color.from_hex("#E97451")
    light_skin = Color.from_hex("#FFCBA4")
    dark_skin = Color.from_hex("#805533")


LEVELS = ["fridge", "fullness", "money", "tiredness"]
LEVEL_COLORS = {
    "fridge": _to_color("#D9DAD2"),
    "fullness": _to_color("#01A638"),
    "money": _to_color("#F1D651"),
    "tiredness": _to_color("#2D383A"),
}

ACTIVITY_COLORS = {
    Activity.NONE: (_n(), _n(), _n()),
    Activity.MOVE: (_c("#E30B5C"), _n(), _n()),
    Activity.WORK: (_c("#8B8680"), _n(), _n()),
    Activity.SHOP: (_c("#A63A79"), _n(), _n()),
    Activity.TALK: (_c("#0095B7"), _c("#FFFFFF"), _c("#000000")),
    Activity.READ: (_c("#AF593E"), _c("#CA3435"), _c("#2D383A")),
    Activity.WTF: (_c("#FF0000"), _n(), _n()),
    Activity.EAT: (_c("#87421F"), _c("#CA3435"), _c("#FFFFFF")),
    Activity.SLEEP: (_c("#0066CC"), _c("#000000"), _n()),
    Activity.TIME_BREAK: (_c("#FFFFFF"), _c("#FFFF66"), _c("#00000044")),
    Activity.ENJOY_DRINK: (_c("#02A4D3"), _c("#87421F"), _c("#FFFFFF")),
    Activity.ENJOY_PLAY: (_c("#02A4D3"), _c("#7A89B8"), _c("#000000")),
    Activity.ENJOY_MUSIC: (_c("#02A4D3"), _c("#2D383A"), _n()),
    Activity.SHARE_LOVE: (_c("#D92121"), _c("#FFFFFF"), _c("#000000")),
    Activity.SHARE_MUSIC: (_c("#D92121"), _c("#FFFFFF"), _c("#000000")),
    Activity.SHARE_WOW: (_c("#D92121"), _c("#FFFFFF"), _c("#000000")),
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

    def __init__(self, batch: Batch, people_group: Group) -> None:
        self.objs = []
        self.kw = dict(batch=batch)
        self.kw_font = dict(
            font_name="Monospace",
            anchor_x="center",
            anchor_y="center",
            **self.kw,
        )
        self.people_group = people_group
        self.trivias_level = defaultdict(float)
        self.activity_sprites = ImageGrid(image_load("textures/activities.png"), 4, 4)
        self.human_sprites = ImageGrid(image_load("textures/human.png"), 2, 2)
        self.learnbar_image = image_load("textures/learnbar.png")
        self.lifeobjs = {}

    def draw_gui(self, people_count, group: GuiGroup):
        kw = dict(**self.kw, group=group)
        kw_font = dict(
            **kw,
            color=(255, 255, 255, 255),
            font_name="Monospace",
            font_size=14,
            bold=True,
        )
        self.people_count = people_count
        self.trivia_dashboard = Label(
            text="",
            multiline=True,
            anchor_x="left",
            anchor_y="top",
            width=600.0,
            x=30.0,
            y=-40.0,
            **kw_font,
        )
        self.objs += [
            Label(
                text="DASHBOARD",
                x=325.0,
                y=-20.0,
                anchor_x="center",
                anchor_y="top",
                **kw_font,
            ),
            BorderedRectangle(
                x=0.0,
                y=-300.0,
                width=650.0,
                height=300.0,
                border=10,
                color=(0, 0, 0, 128),
                border_color=(255, 255, 255),
                **kw,
            ),
        ]

    def draw_path(self, path: dict[tuple[Place, Place], Way], group: Group):
        kw = dict(**self.kw, group=group, width=40.0)
        for way in path.values():
            for i in range(len(way.points) - 1):
                a = way.points[i]
                b = way.points[i + 1]
                color = COLORS.way_a.mix(COLORS.way_b, random()).to_pyglet()
                self.objs.append(Line(a.x, a.y, b.x, b.y, color=color, **kw))

    def draw_places(self, places: list[Place], group: Group):
        kw = dict(**self.kw, group=group)
        kw_font = dict(**self.kw_font, color=(0, 0, 0, 255), font_size=36, group=group)

        for place in places:
            if place.function == PF.CROSSROAD:
                color = COLORS.crossroad_a.mix(COLORS.crossroad_b, random()).to_pyglet()
            else:
                color = COLORS.place_a.mix(COLORS.place_b, random()).to_pyglet()
            p = place.position
            rot = place.rotation
            size = place.box_end - place.box_start
            center = size * 0.5
            start = center + place.box_start

            rect = Rectangle(start.x, start.y, size.x, size.y, color=color, **kw)
            rect.anchor_position = center
            rect.rotation = rot

            self.objs += [
                rect,
                Label(place.name, x=p.x, y=p.y, **kw_font),
            ]

            s = place.room_size
            h = s / 2
            room_color = COLORS.room_a.mix(COLORS.room_b, random()).to_pyglet()
            for room in place.rooms:
                r = room.position
                rect = Rectangle(r.x, r.y, s, s, color=room_color, **kw)
                rect.anchor_position = h, h
                rect.rotation = rot
                self.objs.append(rect)

    def draw_people(self, window: Window, people: list[Human], people_group: Group):
        for index, human in enumerate(people):
            group = HumanGroup(window, index, human, people_group)
            human.position_observers["draw"] = group.update
            self._draw_human(human, group)

    def _draw_human(self, human: Human, group: HumanGroup):
        size = 20
        act_size = size * 1.33
        kw = dict(**self.kw, group=group)
        kw_font = dict(
            **self.kw_font,
            bold=True,
            group=group,
        )

        level_bars = {
            level: BorderedRectangle(
                -size,
                -size * 1.2 - size / 3.8 * (4 - index),
                2 * size * getattr(human.levels, level).value,
                size / 4,
                color=LEVEL_COLORS[level],
                border=5,
                **kw,
            )
            for index, level in enumerate(LEVELS, start=1)
        }

        a = 2 * act_size - size
        act_sprite = Sprite(
            img=self.activity_sprites[0],
            p0=Vec(-size, -size),
            p1=Vec(a, a),
            **kw,
        )

        def level_update(attr, value):
            bar = level_bars[attr]
            bar.width = 2 * size * value
            bar.visible = bar.width > 0.05

        def act_update(activity):
            act_sprite.set_img(self.activity_sprites[activity])
            r, g, b = ACTIVITY_COLORS[activity]
            act_sprite.set_color_r(r)
            act_sprite.set_color_g(g)
            act_sprite.set_color_b(b)

        body = Sprite(
            self.human_sprites[randint(0, 3)],
            p0=Vec(-size, -size),
            p1=Vec(size, size),
            color_r=COLORS.dark_skin.mix(COLORS.light_skin, random()).to_pyglet_alpha(),
            color_g=COLORS.dark_skin.mix(COLORS.light_skin, random()).to_pyglet_alpha(),
            **kw,
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
            body,
            level_bars,
            act_sprite,
        ]

        human.level_observers["draw"] = level_update
        human.activity_observers["draw"] = act_update
        human.knowledge_observers["draw"] = self._trivia_update
        human.talk_observers["draw"] = self._talk_update

    def _trivia_update(self, trivia, new, old):
        diff = new - old
        if diff == 0.0:
            return
        self.trivias_level[trivia] += diff
        c = self.people_count
        gen = zip(
            range(1, 11),
            sorted(self.trivias_level.items(), key=lambda o: o[1], reverse=True),
        )
        self.trivia_dashboard.text = "\n".join(
            self._trivia_label(i, t, percent=l / c * 100) for i, (t, l) in gen
        )

    @staticmethod
    def _trivia_label(i, t, percent) -> str:
        name = f"[{t.category}] {t.name}"
        return f"{i:2}. {name:40}{' ' if len(t.name) <= 40 else '…'} {percent:6.2f} %"

    def _talk_update(self, a: Human, b: Human, trivia: Trivia, state: str):
        kw = dict(**self.kw, group=self.people_group)
        kw_font = dict(
            **self.kw_font, font_size=18, bold=True, color=(0x00, 0x22, 0x55, 0xFF)
        )
        key = (a, b)
        if state == "START" and key not in self.lifeobjs:
            c = (a.position + b.position) * 0.5

            self.lifeobjs[key] = [
                Label(trivia.name, x=c.x, y=c.y, **kw_font),
                AnimatedLine(
                    self.learnbar_image,
                    a.position,
                    b.position,
                    color=(0x33, 0xCC, 0xFF, 0x80),
                    speed=Vec(0.0, 2.0),
                    width=32.0,
                    **kw,
                ),
            ]
        else:
            objs = self.lifeobjs.pop(key, [])
            for obj in objs:
                obj.delete()
