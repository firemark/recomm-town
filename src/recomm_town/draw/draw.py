from collections import defaultdict
from itertools import cycle
from random import randint, random

from pyglet.graphics import Batch, Group
from pyglet.image import ImageGrid, load as image_load, Texture
from pyglet.gl import GL_LINEAR
from pyglet.shapes import Line, Rectangle, BorderedRectangle
from pyglet.window import Window
from pyglet.text import Label

from recomm_town.app import GuiGroup
from recomm_town.draw.track_human import TrackHumanDraw
from recomm_town.draw.utils import crop_label, to_color
from recomm_town.shaders import AnimatedLine, Sprite
from recomm_town.shaders.human_group import HumanGroup
from recomm_town.common import Trivia, Vec
from recomm_town.human import Human, Activity
from recomm_town.shaders.rounded_rectangle import RoundedRectangle
from recomm_town.town import PlaceFunction as PF
from recomm_town.town.place import Place, Way

from recomm_town.draw.consts import (
    ACTIVITY_DARK_COLORS,
    ACTIVITY_LIGHT_COLORS,
    PALLETE,
    PLACE_COLORS,
    TEXTURES,
    FONT,
    COLORS,
    ACTIVITY_TEXTURE_VARIANTS,
)

Texture.default_min_filter = GL_LINEAR
Texture.default_mag_filter = GL_LINEAR


class Draw:
    def __init__(self, batch: Batch, people_group: Group, gui_group: GuiGroup, width: int, height: int) -> None:
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
        self.activity_sprites = ImageGrid(image_load(TEXTURES / "activities.png"), len(Activity), 3)
        self.room_sprites = ImageGrid(image_load(TEXTURES / "rooms.png"), 8, 3)
        self.human_sprite = image_load(TEXTURES / "human.png")
        self.learnbar_image = image_load(TEXTURES / "learnbar.png")
        self.tracked_human: TrackHumanDraw | None = None
        self.lifeobjs = {}
        self.screen_width = width
        self.screen_height = height

    def draw_gui(self, match_time):
        kw = dict(**self.kw, group=self.gui_group)
        kw_font = dict(
            **kw,
            color=COLORS.dashboard_text.to_pyglet_alpha(),
            font_name=FONT,
            font_size=14,
            bold=True,
        )
        self.trivia_dashboard = Label(
            multiline=True,
            anchor_x="left",
            anchor_y="top",
            width=600.0,
            x=30.0,
            y=-40.0,
            **kw_font,
        )
        self.match_time = Label(
            x=20.0,
            y=-20.0,
            anchor_x="left",
            anchor_y="top",
            **kw_font,
        )
        self.tick_tock(match_time)
        self.objs += [
            Label(
                text="DASHBOARD",
                x=325.0,
                y=-20.0,
                anchor_x="center",
                anchor_y="top",
                **kw_font,
            ),
            RoundedRectangle(
                x=0.0,
                y=-300.0,
                width=650.0,
                height=300.0,
                round=32,
                color=COLORS.dashboard_bg.to_pyglet_alpha(0.5),
                **kw,
            ),
        ]

    def on_resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        if self.tracked_human:
            self.tracked_human.on_resize(width)

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
            place_colors = PLACE_COLORS.get(place.look, PLACE_COLORS["default"])
            p = place.position
            rot = place.rotation
            size = place.box_end - place.box_start
            center = p - place.box_start
            start = center + place.box_start

            place_rect = RoundedRectangle(start.x, start.y, size.x, size.y, round=32, color=place_colors.place_color_bg, **kw)
            place_rect.anchor_position = center
            place_rect.rotation = -rot

            self.objs += [
                place_rect,
                Label(place.title, x=p.x, y=p.y, **kw_font),
            ]

            s = place.room_size
            si = s * place_colors.icon_size
            hi = si / 2
            h = s / 2
            index = place_colors.room_texture_id * 3
            for room, index_shift in zip(place.rooms, cycle(list(range(place_colors.textures_len)))):
                r = room.position
                room_body = Sprite(
                    self.room_sprites[index + index_shift],
                    p0=Vec(r.x - hi, r.y - hi),
                    p1=Vec(r.x + hi, r.y + hi),
                    color_r=place_colors.icon_color_r,
                    color_g=place_colors.icon_color_g,
                    color_b=place_colors.icon_color_b,
                    **kw,
                )
                room_rect = RoundedRectangle(
                    r.x, r.y, s, s,
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
            img=self.activity_sprites[0],
            p0=Vec(-a, -a),
            p1=Vec(a, a),
            **kw,
        )

        # def level_update(attr, value):
        #     bar = level_bars[attr]
        #     bar.width = 2 * size * value
        #     bar.visible = bar.width > 0.05

        def act_update(activity):
            variants_count = ACTIVITY_TEXTURE_VARIANTS[activity]
            variant = randint(1, variants_count) - 1
            act_sprite.set_img(self.activity_sprites[activity * 3 + variant])
            r = activity_colors[activity]
            act_sprite.set_color_r(r)
            # act_sprite.set_color_g(g)
            # act_sprite.set_color_b(b)

        body = Sprite(
            self.human_sprite,
            p0=Vec(-size, -size),
            p1=Vec(size, size),
            color_r=skin_color.to_pyglet_alpha(),
            **kw,
        )

        self.objs += [
            Label(  # Name
                human.info.name,
                x=0,
                y=size * 2.5,
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
        self.tracked_human = TrackHumanDraw(human, self.batch, self.gui_group, self.screen_width)

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

            self.lifeobjs[key] = [
                Label(trivia.name, x=c.x, y=c.y, **kw_font),
                AnimatedLine(
                    self.learnbar_image,
                    a.position,
                    b.position,
                    color=PALLETE.l_red.to_pyglet_alpha(0.5),
                    speed=Vec(0.0, 2.0),
                    width=32.0,
                    **kw,
                ),
            ]
        else:
            objs = self.lifeobjs.pop(key, [])
            for obj in objs:
                obj.delete()

