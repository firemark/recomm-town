from pyglet.graphics import Batch
from pyglet.text import Label
from pyglet.text import Label
from recomm_town.common import Vec
from recomm_town.draw.utils import crop_label

from recomm_town.human import Human
from recomm_town.app import GuiGroup

from recomm_town.draw.consts import (
    ACTIVITY_LABELS,
    ACTIVITY_LIGHT_COLORS,
    DASHBOARD_BG,
    DASHBOARD_FG,
    DASHBOARD_FONTS,
    DASHBOARD_INPUT,
    DASHBOARD_WHITE,
    LEVELS,
    LEVELS,
    LEVEL_COLORS,
    ACTIVITY_LABELS,
    TEXTURES,
    dashboard_bar_color,
)
from recomm_town.human.activity import Activity
from recomm_town.shaders.rounded_rectangle import RoundedRectangle
from recomm_town.shaders.arc import Arc
from recomm_town.shaders.sprite import Sprite

from pyglet.image import ImageGrid, load as image_load


class TrackHumanDraw:
    level_sprites = ImageGrid(image_load(TEXTURES / "levels.png"), 4, 1)
    human_sprite = image_load(TEXTURES / "human.png")

    def __init__(self, human: Human, batch: Batch, group: GuiGroup, width: int):
        self.batch = batch
        self.group = group
        self.human = human

        human.level_observers["draw_track"] = self._level_update
        human.activity_observers["draw_track"] = self._act_update
        human.knowledge_observers["draw_track"] = lambda *a: self._trivia_update()
        human.friend_observers["draw_track"] = lambda *a: self._friend_update()

        kw = dict(batch=batch, group=group)
        self.screen_width = width
        x = width - 620.0 - 10
        y = -510.0
        self.objs = {
            "backgrounds": {
                "main": RoundedRectangle(
                    x=x,
                    y=y,
                    round=18,
                    width=610.0,
                    height=500.0,
                    color=DASHBOARD_BG,
                    **kw,
                ),
                "name": RoundedRectangle(
                    x=x + 10.0,
                    y=y + 445.0,
                    round=18,
                    width=210.0,
                    height=50.0,
                    color=DASHBOARD_FG,
                    **kw,
                ),
                "activity": RoundedRectangle(
                    x=x + 230.0,
                    y=y + 445.0,
                    round=18,
                    width=370.0,
                    height=50.0,
                    color=DASHBOARD_FG,
                    **kw,
                ),
                "levels": RoundedRectangle(
                    x=x + 10.0,
                    y=y + 240.0,
                    round=18,
                    width=590.0,
                    height=200.0,
                    color=DASHBOARD_FG,
                    **kw,
                ),
                "knowledge": RoundedRectangle(
                    x=x + 10.0,
                    y=y - 0.0,
                    round=18,
                    width=380.0,
                    height=230.0,
                    color=DASHBOARD_FG,
                    **kw,
                ),
                "friends": RoundedRectangle(
                    x=x + 400.0,
                    y=y - 0.0,
                    round=18,
                    width=200.0,
                    height=230.0,
                    color=DASHBOARD_FG,
                    **kw,
                ),
            },
            "labels": {
                "name": Label(
                    text=human.info.name.upper(),
                    x=x + 20.0,
                    y=y + 485.0,
                    **DASHBOARD_FONTS.NAME,
                    **kw,
                ),
                "level": Label(
                    text=f"LEVELS:",
                    x=x + 20.0,
                    y=y + 430.0,
                    **DASHBOARD_FONTS.LABEL,
                    **kw,
                ),
                "activity": Label(
                    text="ACTIVITY:",
                    x=x + 250.0,
                    y=y + 480.0,
                    **DASHBOARD_FONTS.LABEL,
                    **kw,
                ),
                "knowledge": Label(
                    text="KNOWLEDGE:",
                    x=x + 30.0,
                    y=y + 220.0,
                    **DASHBOARD_FONTS.LABEL,
                    **kw,
                ),
                "friend": Label(
                    text="FRIENDS:",
                    x=x + 430.0,
                    y=y + 220.0,
                    **DASHBOARD_FONTS.LABEL,
                    **kw,
                ),
                "levels": {
                    level: Label(
                        text=f"{level.title()}",
                        x=x - 40.0 + 140.0 * index,
                        y=y + 270.0,
                        color=(*LEVEL_COLORS[level], 255),
                        **(DASHBOARD_FONTS.TEXT | dict(anchor_x="center")),
                        **kw,
                    )
                    for index, level in enumerate(LEVELS, start=1)
                },
            },
            "arcs": {
                level: Arc(
                    x=x - 40.0 + 140 * index,
                    y=y + 340.0,
                    inner_radius=55,
                    outer_radius=65,
                    angle=360.0,
                    color=DASHBOARD_INPUT,
                    **kw,
                )
                for index, level in enumerate(LEVELS, start=1)
            },
            "level_arcs": {
                level: Arc(
                    x=x - 40 + 140 * index,
                    y=y + 340.0,
                    inner_radius=45,
                    outer_radius=65,
                    angle=180.0,
                    color=(*LEVEL_COLORS[level], 255),
                    **kw,
                )
                for index, level in enumerate(LEVELS, start=1)
            },
            "level_symbols": {
                level: Sprite(
                    self.level_sprites[index - 1],
                    p0=Vec(x - 40 + 140 * index, y + 340.0),
                    p1=Vec(x - 40 + 60 + 140 * index, y + 340.0 + 60),
                    anchor=Vec(30, 30),
                    color_r=(*LEVEL_COLORS[level], 255),
                    **kw,
                )
                for index, level in enumerate(LEVELS, start=1)
            },
            "activity": Label(
                x=x + 360.0,
                y=y + 480.0,
                color=DASHBOARD_WHITE,
                **DASHBOARD_FONTS.TEXT,
                **kw,
            ),
            "knowledge": Label(
                x=x + 10.0,
                y=y + 190.0,
                multiline=True,
                width=400.0,
                color=DASHBOARD_WHITE,
                **DASHBOARD_FONTS.TEXT,
                **kw,
            ),
            "friends": Label(
                x=x + 420.0,
                y=y + 190.0,
                multiline=True,
                width=200.0,
                color=DASHBOARD_WHITE,
                **DASHBOARD_FONTS.TEXT,
                **kw,
            ),
        }

        self._trivia_update()
        self._friend_update()
        self._act_update(human.activity)
        for level in LEVELS:
            self._level_update(level, getattr(human.levels, level).value)

    def on_resize(self, width: int):
        self._translate(width, self.objs)
        self.screen_width = width

    def _translate(self, width: int, objs):
        for obj in objs.values():
            if isinstance(obj, dict):
                self._translate(width, obj)
            else:
                obj.x += width - self.screen_width

    def stop(self):
        self.human.level_observers.pop("draw_track", None)
        self.human.activity_observers.pop("draw_track", None)
        self.human.knowledge_observers.pop("draw_track", None)
        self.human.talk_observers.pop("draw_track", None)
        self.human.friend_observers.pop("draw_track", None)
        self.objs.clear()

    def _level_update(self, attr: str, value: float):
        obj = self.objs["level_arcs"][attr]
        obj.angle = 360.0 * value
        obj.color = dashboard_bar_color(value).to_pyglet_alpha()

    def _act_update(self, activity: Activity):
        obj = self.objs["activity"]
        obj.text = ACTIVITY_LABELS[activity]
        obj.color = ACTIVITY_LIGHT_COLORS[activity]

    def _trivia_update(self):
        gen = (
            (trivia, sum(chunks.values()))
            for trivia, chunks in self.human.knowledge.items()
        )
        trivias = (
            f"{index}. {crop_label(trivia.name, size=25):25} " f"{level * 100:3.0f}"
            for (trivia, level), index in zip(
                sorted(gen, key=lambda o: o[1], reverse=True),
                range(1, 8 + 1),
            )
            if level > 1e-2
        )
        self.objs["knowledge"].text = "\n".join(trivias)

    def _friend_update(self):
        gen = self.human.friend_levels.items()
        friends = (
            f"{index}. {friend.info.name}"
            for (friend, level), index in zip(
                sorted(gen, key=lambda o: o[1], reverse=True),
                range(1, 8 + 1),
            )
            if level > 1e-2
        )
        self.objs["friends"].text = "\n".join(friends)
