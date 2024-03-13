from collections import defaultdict
from itertools import cycle
from math import atan2, degrees
from random import randint, random

from pyglet.graphics import Batch, Group
from pyglet.image import Texture
from pyglet.gl import GL_LINEAR
from pyglet.shapes import Line
from pyglet.window import Window
from pyglet.text import Label

from recomm_town.app import GuiGroup
from recomm_town.draw.textures import (
    ACTIVITY_SPRITES,
    BLOB_SPRITES,
    HUMAN_SPRITE,
    LEARNBAR_IMAGE,
    ROOM_SPRITES,
)
from recomm_town.draw.track_human import TrackHumanDraw
from recomm_town.draw.utils import crop_label, to_color
from recomm_town.shaders import AnimatedLine, Sprite
from recomm_town.shaders.curve_line import CurveLine
from recomm_town.shaders.human_group import HumanGroup
from recomm_town.common import Trivia, Vec
from recomm_town.human import Human
from recomm_town.shaders.rounded_rectangle import RoundedRectangle
from recomm_town.town.place import Place, Way

from recomm_town.draw.consts import (
    ACTIVITY_DARK_COLORS,
    ACTIVITY_LIGHT_COLORS,
    DASHBOARD_BG,
    DASHBOARD_FONTS,
    DASHBOARD_WHITE,
    PALLETE,
    PLACE_COLORS,
    FONT,
    COLORS,
    ACTIVITY_TEXTURE_VARIANTS,
)

Texture.default_min_filter = GL_LINEAR
Texture.default_mag_filter = GL_LINEAR


class Draw:
    def __init__(
        self,
        batch: Batch,
        people_group: Group,
        gui_group: GuiGroup,
        width: int,
        height: int,
    ) -> None:
        self.objs = []
        self.batch = batch
        self.gui_group = gui_group
        self.kw = dict(batch=batch)
        self.kw_font = dict(
            font_name=FONT,
            anchor_x="center",
            anchor_y="center",
            **self.kw,
        )
        self.people_group = people_group
        self.trivias_level = defaultdict(float)
        self.tracked_human: TrackHumanDraw | None = None
        self.lifeobjs = {}
        self.screen_width = width
        self.screen_height = height

    def draw_gui(self, match_time):
        kw = dict(**self.kw, group=self.gui_group)
        self.trivia_dashboard = Label(
            multiline=True,
            width=600.0,
            x=30.0,
            y=-50.0,
            color=DASHBOARD_WHITE,
            **DASHBOARD_FONTS.TEXT,
            **kw,
        )
        self.match_time = Label(
            x=20.0,
            y=-20.0,
            **DASHBOARD_FONTS.LABEL,
            **kw,
        )
        self.tick_tock(match_time)
        self.objs += [
            Label(
                text="DASHBOARD",
                x=325.0,
                y=-20.0,
                **(DASHBOARD_FONTS.NAME | dict(anchor_x="center", anchor_y="top")),
                **kw,
            ),
            RoundedRectangle(
                x=10.0,
                y=-310.0,
                width=650.0,
                height=300.0,
                round=18,
                color=DASHBOARD_BG,
                **kw,
            ),
        ]

    def on_resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        if self.tracked_human:
            self.tracked_human.on_resize(width)

    def draw_path(self, path: dict[tuple[Place, Place], Way], group: Group):
        kw = dict(**self.kw, group=group, width=50.0)
        for way in path.values():
            for i in range(len(way.points) - 1):
                a = way.points[i]
                b = way.points[i + 1]
                color = COLORS.way_a.mix(COLORS.way_b, random()).to_pyglet()
                self.objs.append(Line(a.x, a.y, b.x, b.y, color=color, **kw))

    def draw_blobs(self, boundaries, group: Group):
        start = boundaries[0]
        diff = boundaries[1] - boundaries[0]
        kw = dict(**self.kw, group=group)
        for i in range(20):
            position = Vec(start.x + random() * diff.x, start.y + random() * diff.y)
            half_size = 256.0 + random() * 256.0
            color = PALLETE.d_grass.mix(PALLETE.l_grass, 0.6 + random() * 0.4)
            self.objs.append(
                Sprite(
                    BLOB_SPRITES[randint(0, 3)],
                    p0=position - half_size,
                    p1=position + half_size,
                    color_r=color.to_pyglet_alpha(),
                    **kw,
                )
            )

    def draw_places(self, places: list[Place], group: Group):
        kw = dict(**self.kw, group=group)
        kw_font = dict(**self.kw_font, color=(0, 0, 0, 255), font_size=36, group=group)
        margin = 20
        gate_width = 85

        for place in places:
            place_colors = PLACE_COLORS.get(place.look, PLACE_COLORS["default"])
            p = place.position
            rot = place.rotation
            box_start = place.box_start - margin
            box_end = place.box_end + margin
            size = box_end - box_start
            center = p - box_start

            place_rect = RoundedRectangle(
                p.x,
                p.y,
                size.x,
                size.y,
                round=32,
                color=place_colors.place_color_bg,
                **kw,
            )
            place_rect.anchor_position = center
            place_rect.rotation = -rot

            border_kw = dict(
                x=p.x,
                y=p.y,
                thickness=10,
                round=32,
                color=place_colors.border_color,
                rotation=-rot,
                **kw,
            )

            border_ld = CurveLine(
                width=center.x - gate_width,
                height=center.y - gate_width,
                anchor_position=Vec(center.x, center.y),
                **border_kw,
            )

            border_lu = CurveLine(
                width=center.x - gate_width,
                height=center.y - size.y + gate_width,
                anchor_position=Vec(center.x, center.y - size.y),
                **border_kw,
            )

            border_ru = CurveLine(
                width=center.x - size.x + gate_width,
                height=center.y - size.y + gate_width,
                anchor_position=Vec(center.x - size.x, center.y - size.y),
                **border_kw,
            )

            border_rd = CurveLine(
                width=center.x - size.x + gate_width,
                height=center.y - gate_width,
                anchor_position=Vec(center.x - size.x, center.y),
                **border_kw,
            )

            self.objs += [
                place_rect,
                border_ld,
                border_lu,
                border_ru,
                border_rd,
                Label(place.title, x=p.x, y=p.y, **kw_font),
            ]

            s = place.room_size
            si = s * place_colors.icon_size
            hi = si / 2
            h = s / 2
            index = place_colors.room_texture_id * 3
            for room, index_shift in zip(
                place.rooms, cycle(list(range(place_colors.textures_len)))
            ):
                r = room.position
                room_body = Sprite(
                    ROOM_SPRITES[index + index_shift],
                    p0=Vec(r.x - hi, r.y - hi),
                    p1=Vec(r.x + hi, r.y + hi),
                    color_r=place_colors.icon_color_r,
                    color_g=place_colors.icon_color_g,
                    color_b=place_colors.icon_color_b,
                    **kw,
                )
                room_rect = RoundedRectangle(
                    r.x,
                    r.y,
                    s,
                    s,
                    color=place_colors.room_color_bg,
                    round=16,
                    **kw,
                )
                room_rect.anchor_position = h, h
                room_rect.rotation = room.rotation
                self.objs += [room_body, room_rect]

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

        # level_bars = {
        #     level: BorderedRectangle(
        #         -size,
        #         -size * 1.2 - size / 3.8 * (4 - index),
        #         2 * size * getattr(human.levels, level).value,
        #         size / 4,
        #         color=LEVEL_COLORS[level],
        #         border=5,
        #         **kw,
        #     )
        #     for index, level in enumerate(LEVELS, start=1)
        # }

        skin_lightness = random()
        if skin_lightness > 0.6:
            activity_colors = ACTIVITY_LIGHT_COLORS
        else:
            activity_colors = ACTIVITY_DARK_COLORS
        skin_color = COLORS.light_skin.mix(COLORS.dark_skin, skin_lightness)
        a = size * 0.6
        act_sprite = Sprite(
            img=ACTIVITY_SPRITES[0],
            p0=Vec(-a, -a),
            p1=Vec(a, a),
            **kw,
        )

        # def level_update(attr, value):
        #     bar = level_bars[attr]
        #     bar.width = 2 * size * value
        #     bar.visible = bar.width > 0.05

        act_sprite_callbacks = [
            act_sprite.set_color_r,
            act_sprite.set_color_g,
            act_sprite.set_color_b,
        ]

        def act_update(activity):
            variants_count = ACTIVITY_TEXTURE_VARIANTS[activity]
            variant = randint(1, variants_count) - 1
            act_sprite.set_img(ACTIVITY_SPRITES[activity * 3 + variant])
            colors = activity_colors[activity]
            if isinstance(colors, tuple):
                colors = [colors]
            for cb, color in zip(act_sprite_callbacks, colors):
                cb(color)

        body = Sprite(
            HUMAN_SPRITE,
            p0=Vec(-size, -size),
            p1=Vec(size, size),
            color_r=skin_color.to_pyglet_alpha(),
            **kw,
        )

        self.objs += [
            Label(  # Name
                human.info.name,
                x=0,
                y=size * 1.5,
                font_size=14,
                color=to_color("#2D383A") + (255,),
                **kw_font,
            ),
            body,
            # level_bars,
            act_sprite,
        ]

        # human.level_observers["draw"] = level_update
        human.activity_observers["draw"] = act_update
        human.knowledge_observers["draw"] = self._trivia_update
        human.talk_observers["draw"] = self._talk_update

    def track_human(self, human: Human | None):
        if self.tracked_human is not None:
            self.tracked_human.stop()
        if human is None:
            return
        self.tracked_human = TrackHumanDraw(
            human, self.batch, self.gui_group, self.screen_width
        )

    def tick_tock(self, match_time: int):
        minutes = match_time // 60
        seconds = match_time % 60
        self.match_time.text = f"{minutes:02d}:{seconds:02d}"

    def _trivia_update(self, position, trivia_chunk, new, old):
        diff = new - old
        if diff == 0.0:
            return
        trivia, chunk_id = trivia_chunk
        self.trivias_level[trivia] += diff
        gen = zip(
            range(1, 11),
            sorted(self.trivias_level.items(), key=lambda o: o[1], reverse=True),
        )
        self.trivia_dashboard.text = "\n".join(
            self._trivia_label(i, trivia, level * 100) for i, (trivia, level) in gen
        )

    @staticmethod
    def _trivia_label(index, trivia, points) -> str:
        name = f"[{trivia.category}] {trivia.name}"
        return f"{index:2}. {crop_label(name, size=40):40} {points:6.0f}"

    def _talk_update(self, a: Human, b: Human, trivia: Trivia | None, state: str):
        kw = dict(**self.kw, group=self.people_group)
        kw_font = dict(
            **self.kw_font,
            font_size=18,
            bold=True,
            color=PALLETE.white.to_pyglet_alpha(),
        )
        key = (a, b)
        if state == "START" and trivia and key not in self.lifeobjs:
            c = (a.position + b.position) * 0.5
            diff = b.position - a.position
            if diff.x < 0:
                diff = -diff

            label = Label(trivia.name, x=c.x, y=c.y, **kw_font)
            label.rotation = -degrees(atan2(diff.y, diff.x))
            line_length = diff.length() - 32

            objs = [
                AnimatedLine(
                    LEARNBAR_IMAGE,
                    a.position,
                    b.position,
                    color=PALLETE.l_red.to_pyglet_alpha(),
                    speed=Vec(0.0, 2.0),
                    width=32.0,
                    **kw,
                ),
            ]

            if line_length > 0:
                while label.font_size > 8 and label.content_width > line_length:
                    label.font_size -= 2

                if label.font_size > 8:
                    objs.append(label)

            self.lifeobjs[key] = objs
        else:
            objs = self.lifeobjs.pop(key, [])
            for obj in objs:
                obj.delete()
