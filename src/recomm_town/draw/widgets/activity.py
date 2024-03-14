from pyglet.text import Label
from pyglet.text import Label
from recomm_town.common import Vec

from recomm_town.draw.consts import (
    ACTIVITY_CFG,
    DASHBOARD_FONTS,
    DASHBOARD_WHITE,
)
from recomm_town.human.activity import Activity
from recomm_town.shaders.arc import Arc
from recomm_town.shaders.sprite import Sprite
from recomm_town.draw.textures import HUMAN_SPRITE, ACTIVITY_SPRITES


class ActivityWidget:

    def __init__(self, x, y, batch, group):
        kw = dict(batch=batch, group=group)
        self.label = Label(
            x=x + 50.0,
            y=y,
            color=DASHBOARD_WHITE,
            **DASHBOARD_FONTS.TEXT,
            **kw,
        )

        self.bg = Sprite(
            HUMAN_SPRITE,
            p0=Vec(x, y),
            p1=Vec(x + 40, y + 40),
            anchor=Vec(0, 30),
            **kw,
        )

        self.symbol = Sprite(
            ACTIVITY_SPRITES[0],
            p0=Vec(x, y),
            p1=Vec(x + 30, y + 30),
            anchor=Vec(-5, 25),
            color_r=(0, 0, 0, 255),
            **kw,
        )

    def update(self, activity: Activity):
        cfg = ACTIVITY_CFG[activity]
        color = cfg.dashboard_color
        self.label.text = cfg.label
        self.label.color = color
        self.symbol.set_img(ACTIVITY_SPRITES[activity * 3])
        self.bg.set_color_r(color)
