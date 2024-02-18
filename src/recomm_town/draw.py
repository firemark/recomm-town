from collections import defaultdict
from math import fmod, sqrt
from random import randint, random

from pyglet.graphics import Batch, Group
from pyglet.sprite import (
    Sprite,
    SpriteGroup,
    get_default_shader,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_TRIANGLES,
)
from pyglet.image import ImageGrid, load as image_load
from pyglet.shapes import Line, Rectangle, BorderedRectangle
from pyglet.window import Window
from pyglet.text import Label
from pyglet import clock

from recomm_town.app import GuiGroup
from recomm_town.common import Color, Trivia
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
    Activity.NONE: _to_color("#000000"),
    Activity.MOVE: _to_color("#E30B5C"),
    Activity.WORK: _to_color("#8B8680"),
    Activity.SHOP: _to_color("#A63A79"),
    Activity.TALK: _to_color("#FFFFFF"),
    Activity.READ: _to_color("#CA3435"),
    Activity.WTF: _to_color("#FF0000"),
    Activity.EAT: _to_color("#CA3435"),
    Activity.SLEEP: _to_color("#0066CC"),
    Activity.TIME_BREAK: _to_color("#FFFFFF"),
    Activity.ENJOY_DRINK: _to_color("#02A4D3"),
    Activity.ENJOY_PLAY: _to_color("#02A4D3"),
    Activity.ENJOY_MUSIC: _to_color("#02A4D3"),
    Activity.SHARE_LOVE: _to_color("#FE6F5E"),
    Activity.SHARE_MUSIC: _to_color("#FE6F5E"),
    Activity.SHARE_WOW: _to_color("#FE6F5E"),
}


class AnimatedLine:
    _vertex_list = None
    group_class = SpriteGroup

    def __init__(
        self,
        img,
        x0,
        y0,
        x1,
        y1,
        width=1,
        move_x=0,
        move_y=1,
        dt=0.05,
        blend_src=GL_SRC_ALPHA,
        blend_dest=GL_ONE_MINUS_SRC_ALPHA,
        batch=None,
        group=None,
        color=(255, 255, 255, 255),
    ):
        diff_x = x0 - x1
        diff_y = y0 - y1
        length = sqrt(diff_x**2 + diff_y**2)
        diff_max = max(abs(diff_x), abs(diff_y))
        diff_x *= width / diff_max / 2
        diff_y *= width / diff_max / 2

        # fmt: off
        self._v = (
            x0 - diff_y, y0 + diff_x, 0.0,
            x0 + diff_y, y0 - diff_x, 0.0,
            x1 + diff_y, y1 - diff_x, 0.0,
            x1 - diff_y, y1 + diff_x, 0.0,
        )
        # fmt: on
        self._texture = img.get_texture()
        self._program = get_default_shader()
        self._repeat_x = 1.0
        self._repeat_y = length / width
        self._move_x = move_x
        self._move_y = move_y
        self._color = color

        self.batch = batch
        self.group = self.group_class(
            self._texture, blend_src, blend_dest, self._program, group
        )
        self.dt = dt
        self.t = 0.0
        self._create_vertex_list()
        clock.schedule_interval(self._animate, dt)

    def _create_vertex_list(self):
        tx = self._move_x * self.t
        ty = self._move_y * self.t
        ttx = tx + self._repeat_x
        tty = ty + self._repeat_y
        tex_coords = (tx, ty, 0.0) + (ttx, ty, 0.0) + (ttx, tty, 0.0) + (tx, tty, 0.0)
        self._vertex_list = self._program.vertex_list_indexed(
            4,
            GL_TRIANGLES,
            [0, 1, 2, 0, 2, 3],
            self.batch,
            self.group,
            position=("f", self._v),
            colors=("Bn", self._color * 4),
            translate=("f", (0, 0, 0) * 4),
            scale=("f", (1.0, 1.0) * 4),
            rotation=("f", (0.0,) * 4),
            tex_coords=("f", tex_coords),
        )

    def draw(self):
        if self._vertex_list is None:
            return
        self.group.set_state_recursive()
        self._vertex_list.draw(GL_TRIANGLES)
        self.group.unset_state_recursive()

    def __del__(self):
        try:
            if self._vertex_list is not None:
                self._vertex_list.delete()
        except:
            pass

    def _animate(self, dt):
        if self._vertex_list is None:
            return  # Deleted in event handler.
        self.t = fmod(self.t + dt, 1.0)
        self._vertex_list.delete()
        self._create_vertex_list()

    def delete(self):
        clock.unschedule(self._animate)
        if self._vertex_list is not None:
            self._vertex_list.delete()
        self._vertex_list = None
        self._texture = None
        self._group = None


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

    def draw_path(self, path: list[Way], group: Group):
        kw = dict(**self.kw, group=group, width=50.0)
        for way in path:
            a = way.a.position
            b = way.b.position
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
            start = place.box_start
            size = place.box_end - start

            self.objs += [
                Rectangle(start.x, start.y, size.x, size.y, color=color, **kw),
                Label(place.name, x=p.x, y=p.y, **kw_font),
            ]

            s = place.room_size
            h = s / 2
            room_color = COLORS.room_a.mix(COLORS.room_b, random()).to_pyglet()
            for room in place.rooms:
                r = room.position - h
                self.objs.append(Rectangle(r.x, r.y, s, s, color=room_color, **kw))

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
                -size * 1.2 - size / 3.8 * (4 - index),
                2 * size * getattr(human.levels, level).value,
                size / 4,
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
            bar.visible = bar.width > 0.05

        def act_update(activity):
            act_sprite.image = self.activity_sprites[activity]
            act_sprite.color = ACTIVITY_COLORS[activity]

        body = Sprite(self.human_sprites[randint(0, 3)], x=-size, y=-size, **kw)
        body.scale = size / 32
        body.color = COLORS.dark_skin.mix(COLORS.light_skin, random()).to_pyglet()

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
                    a.position.x,
                    a.position.y,
                    b.position.x,
                    b.position.y,
                    color=(0x33, 0xCC, 0xFF, 0x80),
                    move_y=2,
                    width=32,
                    **kw,
                ),
            ]
        else:
            objs = self.lifeobjs.pop(key, [])
            for obj in objs:
                obj.delete()
