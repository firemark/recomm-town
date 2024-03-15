from recomm_town.draw.consts import DASHBOARD_FONTS
from pyglet.text import Label
from pyglet.text import Label
from recomm_town.common import Vec

from recomm_town.shaders.arc import Arc
from recomm_town.shaders.sprite import Sprite

from recomm_town.draw.consts import (
    DASHBOARD_FONTS,
    DASHBOARD_INPUT,
    dashboard_bar_color,
    LevelCfg,
)
from recomm_town.draw.textures import LEVEL_SPRITES


class LevelArcWidget:

    def __init__(self, x, y, cfg: LevelCfg, batch, group):
        kw = dict(batch=batch, group=group)
        self.label = Label(
            text=cfg.label,
            x=x,
            y=y - 65.0,
            color=cfg.color,
            **(DASHBOARD_FONTS.TEXT | dict(anchor_x="center")),
            **kw,
        )
        self.grey_arc = Arc(
            x=x,
            y=y,
            inner_radius=55,
            outer_radius=65,
            angle=360.0,
            color=DASHBOARD_INPUT,
            **kw,
        )

        self.symbol = Sprite(
            LEVEL_SPRITES[cfg.texture_index],
            p0=Vec(x, y),
            p1=Vec(x + 60, y + 60),
            anchor=Vec(30, 30),
            color_r=cfg.color,
            **kw,
        )

        self.level_arc = Arc(
            x=x,
            y=y,
            inner_radius=45,
            outer_radius=65,
            angle=180.0,
            color=cfg.color,
            **kw,
        )

    def update(self, value: float):
        self.level_arc.angle = 360.0 * value
        self.level_arc.color = dashboard_bar_color(value).to_pyglet_alpha()
