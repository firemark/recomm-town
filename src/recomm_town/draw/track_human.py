from pyglet.graphics import Batch
from pyglet.shapes import BorderedRectangle
from pyglet.text import Label
from pyglet.text import Label
from recomm_town.draw.utils import crop_label

from recomm_town.human import Human
from recomm_town.app import GuiGroup

from recomm_town.draw.consts import (
    ACTIVITY_LABELS,
    COLORS,
    FONT,
    LEVELS,
    LEVELS,
    LEVEL_COLORS,
    ACTIVITY_LABELS,
)
from recomm_town.human.activity import Activity
from recomm_town.shaders.rounded_rectangle import RoundedRectangle


class TrackHumanDraw:
    def __init__(self, human: Human, batch: Batch, group: GuiGroup, width: int):
        self.batch = batch
        self.group = group
        self.human = human

        human.level_observers["draw_track"] = self._level_update
        human.activity_observers["draw_track"] = self._act_update
        human.knowledge_observers["draw_track"] = lambda *a: self._trivia_update()
        human.friend_observers["draw_track"] = lambda *a: self._friend_update()

        kw = dict(batch=batch, group=group)
        kw_font = dict(
            **kw,
            font_name=FONT,
            font_size=14,
            bold=True,
            anchor_x="left",
            anchor_y="top",
        )

        df_color = COLORS.dashboard_text.to_pyglet_alpha()
        self.screen_width = width
        x = width - 850.0
        y = -300.0
        self.objs = {
            "background": RoundedRectangle(
                x=x,
                y=y,
                round=32,
                width=850.0,
                height=300.0,
                # border=10,
                color=COLORS.dashboard_bg.to_pyglet_alpha(0.5),
                # border_color=COLORS.dashboard_text.to_pyglet(),
                **kw,
            ),
            "labels": {
                "name": Label(
                    text=f"Name: {human.info.name}",
                    x=x + 20.0,
                    y=y + 280.0,
                    color=df_color,
                    **kw_font,
                ),
                "level": Label(
                    text=f"Levels:",
                    x=x + 20.0,
                    y=y + 240.0,
                    **kw_font,
                ),
                "levels": {
                    level: Label(
                        text=f"{level.title()}:",
                        x=x + 20.0,
                        y=y + 240.0 - 30.0 * index,
                        color=(*LEVEL_COLORS[level], 255),
                        **kw_font,
                    )
                    for index, level in enumerate(LEVELS, start=1)
                },
                "activity": Label(
                    text="Activity:",
                    x=x + 250.0,
                    y=y + 280.0,
                    color=df_color,
                    **kw_font,
                ),
                "knowledge": Label(
                    text="Knowledge:",
                    x=x + 250.0,
                    y=y + 240.0,
                    color=df_color,
                    **kw_font,
                ),
                "friend": Label(
                    text="Friends:",
                    x=x + 650.0,
                    y=y + 240.0,
                    color=df_color,
                    **kw_font,
                ),
            },
            "levels": {
                level: Label(
                    x=x + 150.0,
                    y=y + 240.0 - 30.0 * index,
                    color=(*LEVEL_COLORS[level], 255),
                    **kw_font,
                )
                for index, level in enumerate(LEVELS, start=1)
            },
            "activity": Label(
                x=x + 360.0,
                y=y + 280.0,
                **kw_font,
            ),
            "knowledge": Label(
                x=x + 250.0,
                y=y + 210.0,
                multiline=True,
                width=400.0,
                **kw_font,
            ),
            "friends": Label(
                x=x + 650.0,
                y=y + 210.0,
                multiline=True,
                width=200.0,
                **kw_font,
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
        self.objs["levels"][attr].text = f"{value * 100.0:3.0f} %"

    def _act_update(self, activity: Activity):
        self.objs["activity"].text = ACTIVITY_LABELS[activity].format()

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
