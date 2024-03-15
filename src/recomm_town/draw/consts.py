from dataclasses import InitVar, dataclass
import os
import platform
from pathlib import Path

from recomm_town.common import Color, Vec
from recomm_town.human import Activity
from recomm_town.draw.utils import to_color, c, n
from recomm_town.town.place import PlaceFunction


TEXTURES = Path(os.environ["ASSETS"]) / "textures"
FONT = "Arial" if platform.system() == "Windows" else "Monospace"


class PALLETE:
    road = Color.from_hex("#F2F3ED")
    l_grass = Color.from_hex("#C9DBB3")
    d_grass = Color.from_hex("#97BFA5")
    i_yellow = Color.from_hex("#F0EADB")
    l_yellow = Color.from_hex("#FDC362")
    d_yellow = Color.from_hex("#D68663")
    i_red = Color.from_hex("#F0DBDB")
    l_red = Color.from_hex("#FF4D4D")
    d_red = Color.from_hex("#AC3232")
    i_green = Color.from_hex("#E0F0DB")
    l_green = Color.from_hex("#60C757")
    d_green = Color.from_hex("#4A8545")
    i_purple = Color.from_hex("#EEDBF0")
    l_purple = Color.from_hex("#BE46B6")
    d_purple = Color.from_hex("#613C86")
    i_blue = Color.from_hex("#DBE6F0")
    l_blue = Color.from_hex("#76CAE9")
    d_blue = Color.from_hex("#328EB3")
    l_grey = Color.from_hex("#C4C4C4")
    d_grey = Color.from_hex("#999999")
    l_skin = Color.from_hex("#FFF5D1")
    d_skin = Color.from_hex("#6B4C2E")
    white = Color.from_hex("#FFFFFF")
    black = Color.from_hex("#000000")


class COLORS:
    dashboard_text = Color.from_hex("#FFFFFF")
    dashboard_bg = Color.from_hex("#000000")
    room_a = Color.from_hex("#50BFE6")
    room_b = Color.from_hex("#01A638")
    place_a = Color.from_hex("#EED9C4")
    place_b = Color.from_hex("#C0D5F0")
    crossroad_a = PALLETE.road
    crossroad_b = PALLETE.road
    way_a = PALLETE.road
    way_b = PALLETE.road
    light_skin = PALLETE.l_skin
    dark_skin = PALLETE.d_skin


@dataclass(frozen=True)
class IconColor:
    r: tuple[int, int, int, int] = n()
    g: tuple[int, int, int, int] = n()
    b: tuple[int, int, int, int] = n()


@dataclass(frozen=True)
class PlaceCfg:
    room_texture_id: int = 0
    textures_len: int = 1
    place_color_bg: tuple[int, int, int, int] = PALLETE.road.to_pyglet_alpha()
    border_color: tuple[int, int, int, int] = n()
    room_color_bg: tuple[int, int, int, int] = n()
    icon_size: float = 0.6
    icon_color: IconColor = IconColor()


@dataclass(frozen=True)
class ActCfg:
    label: str
    icon_size: float = 0.6
    icon_shift: Vec = Vec(0.0, 0.0)
    variants: int = 1
    light_icon_color: IconColor = IconColor()
    dashboard_color: tuple[int, int, int, int] = n()
    dark_icon_color: IconColor | None = None

    def __post_init__(self):
        if self.dark_icon_color is None:
            object.__setattr__(self, "dark_icon_color", self.light_icon_color)
        if self.dashboard_color == n():
            object.__setattr__(self, "dashboard_color", self.light_icon_color.r)

    def find_icon_color(self, skin_lightness: float) -> IconColor:
        if skin_lightness > 0.5:
            return self.light_icon_color
        else:
            return self.dark_icon_color  # type: ignore


PLACE_CFG = {
    "default": PlaceCfg(),
    "garden": PlaceCfg(
        room_texture_id=1,
        textures_len=2,
        place_color_bg=PALLETE.road.to_pyglet_alpha(),
        border_color=PALLETE.d_grass.to_pyglet_alpha(),
        icon_size=1.0,
        icon_color=IconColor(
            r=PALLETE.d_grass.to_pyglet_alpha(),
            g=PALLETE.l_grass.to_pyglet_alpha(),
        ),
    ),
    "museum": PlaceCfg(
        room_texture_id=2,
        place_color_bg=c("#D0BDE3"),
        room_color_bg=c("#7A58A0"),
        border_color=c("#6C4691"),
        icon_color=IconColor(
            g=c("#D686D4"),
            b=c("#CE6EC8"),
        ),
    ),
    "pub": PlaceCfg(
        room_texture_id=3,
        textures_len=2,
        place_color_bg=c("#EFE4C8"),
        border_color=c("#ECA756"),
        room_color_bg=c("#ECA756"),
        icon_color=IconColor(
            r=c("#D68663"),
            g=c("#FDC362"),
            b=c("#FFD199"),
        ),
    ),
    "work": PlaceCfg(
        place_color_bg=PALLETE.l_grey.to_pyglet_alpha(),
        room_color_bg=PALLETE.d_grey.to_pyglet_alpha(),
        border_color=PALLETE.d_grey.to_pyglet_alpha(),
    ),
    "home": PlaceCfg(
        room_texture_id=4,
        textures_len=1,
        place_color_bg=PALLETE.i_blue.to_pyglet_alpha(),
        room_color_bg=PALLETE.l_blue.to_pyglet_alpha(),
        border_color=PALLETE.l_blue.to_pyglet_alpha(),
        icon_size=0.7,
        icon_color=IconColor(
            r=PALLETE.d_blue.to_pyglet_alpha(),
        ),
    ),
    "shop": PlaceCfg(
        place_color_bg=PALLETE.i_purple.to_pyglet_alpha(),
        room_color_bg=PALLETE.l_purple.to_pyglet_alpha(),
        border_color=PALLETE.l_purple.to_pyglet_alpha(),
    ),
    "entertainment": PlaceCfg(
        place_color_bg=PALLETE.l_blue.to_pyglet_alpha(),
        room_color_bg=PALLETE.d_blue.to_pyglet_alpha(),
        border_color=PALLETE.d_blue.to_pyglet_alpha(),
    ),
    "community": PlaceCfg(
        room_texture_id=2,
        place_color_bg=PALLETE.l_blue.to_pyglet_alpha(),
        room_color_bg=PALLETE.d_blue.to_pyglet_alpha(),
        border_color=PALLETE.d_blue.to_pyglet_alpha(),
        icon_color=IconColor(
            g=c("#869DD6"),
            b=c("#6E89CE"),
        ),
    ),
}


@dataclass(frozen=True)
class LevelCfg:
    attr: str
    label: str
    color: tuple[int, int, int, int]
    texture_index: int


LEVELS = [
    LevelCfg("fridge", "Fridge", c("#D9DAD2"), 0),
    LevelCfg("satiety", "Satiety", c("#9CE256"), 1),
    LevelCfg("money", "Wealth", c("#F1D651"), 2),
    LevelCfg("energy", "Energy", c("#FF5349"), 3),
]

ACTIVITY_CFG = {
    Activity.NONE: ActCfg(label="-"),
    Activity.MOVE: ActCfg(
        label="Moving",
        light_icon_color=IconColor(PALLETE.l_red.to_pyglet_alpha()),
    ),
    Activity.WORK: ActCfg(
        label="Working",
        dashboard_color=PALLETE.l_grey.to_pyglet_alpha(),
        light_icon_color=IconColor(PALLETE.d_grey.to_pyglet_alpha()),
        dark_icon_color=IconColor(PALLETE.white.to_pyglet_alpha()),
    ),
    Activity.SHOP: ActCfg(
        label="Shopping",
        dashboard_color=PALLETE.l_grey.to_pyglet_alpha(),
        light_icon_color=IconColor(PALLETE.d_grey.to_pyglet_alpha()),
        dark_icon_color=IconColor(PALLETE.white.to_pyglet_alpha()),
    ),
    Activity.TALK: ActCfg(
        label="Seeking to talk",
        icon_size=1.0,
        icon_shift=Vec(0.0, -0.25),
        light_icon_color=IconColor(
            r=PALLETE.l_blue.to_pyglet_alpha(),
            g=PALLETE.white.to_pyglet_alpha(),
            b=PALLETE.black.to_pyglet_alpha(),
        ),
    ),
    Activity.READ: ActCfg(
        label="Reading a book",
        dashboard_color=PALLETE.l_yellow.to_pyglet_alpha(),
        light_icon_color=IconColor(PALLETE.d_yellow.to_pyglet_alpha()),
        dark_icon_color=IconColor(PALLETE.l_yellow.to_pyglet_alpha()),
    ),
    Activity.RADIO: ActCfg(
        label="Listening a radio",
        dashboard_color=PALLETE.l_yellow.to_pyglet_alpha(),
        light_icon_color=IconColor(PALLETE.d_yellow.to_pyglet_alpha()),
        dark_icon_color=IconColor(PALLETE.l_yellow.to_pyglet_alpha()),
    ),
    Activity.TV: ActCfg(
        label="Watching a TV",
        dashboard_color=PALLETE.l_yellow.to_pyglet_alpha(),
        light_icon_color=IconColor(PALLETE.d_yellow.to_pyglet_alpha()),
        dark_icon_color=IconColor(PALLETE.l_yellow.to_pyglet_alpha()),
    ),
    Activity.WTF: ActCfg(
        label="Confused",
        icon_size=1.0,
        variants=3,
        light_icon_color=IconColor(PALLETE.l_red.to_pyglet_alpha()),
    ),
    Activity.EAT: ActCfg(
        label="Eating",
        variants=3,
        dashboard_color=PALLETE.l_green.to_pyglet_alpha(),
        light_icon_color=IconColor(PALLETE.d_green.to_pyglet_alpha()),
        dark_icon_color=IconColor(PALLETE.i_green.to_pyglet_alpha()),
    ),
    Activity.SLEEP: ActCfg(
        label="Sleeping",
        icon_size=1.0,
        icon_shift=Vec(0.0, -0.20),
        light_icon_color=IconColor(
            r=PALLETE.l_blue.to_pyglet_alpha(),
            g=PALLETE.black.to_pyglet_alpha(),
        ),
        dark_icon_color=IconColor(
            r=PALLETE.l_blue.to_pyglet_alpha(),
            g=PALLETE.white.to_pyglet_alpha(),
        ),
    ),
    Activity.TIME_BREAK: ActCfg(
        label="Waiting",
        dashboard_color=PALLETE.white.to_pyglet_alpha(),
        light_icon_color=IconColor(PALLETE.black.to_pyglet_alpha()),
        dark_icon_color=IconColor(PALLETE.white.to_pyglet_alpha()),
    ),
    Activity.ENJOY: ActCfg(
        label="Enjoy",
        variants=2,
        dashboard_color=PALLETE.l_blue.to_pyglet_alpha(),
        light_icon_color=IconColor(PALLETE.d_blue.to_pyglet_alpha()),
        dark_icon_color=IconColor(PALLETE.l_blue.to_pyglet_alpha()),
    ),
    Activity.SHARE: ActCfg(
        label="Talking & Sharing",
        icon_size=1.0,
        icon_shift=Vec(0.0, -0.25),
        variants=3,
        light_icon_color=IconColor(
            r=PALLETE.l_red.to_pyglet_alpha(),
            g=PALLETE.white.to_pyglet_alpha(),
            b=PALLETE.black.to_pyglet_alpha(),
        ),
    ),
    Activity.IDEA: ActCfg(
        label="Gathering ideas",
        light_icon_color=IconColor(PALLETE.l_purple.to_pyglet_alpha()),
    ),
}


PLACE_LABEL_BG = c("#00000040")
DASHBOARD_BG = c("#00000072")
DASHBOARD_FG = c("#89917E4C")
DASHBOARD_INPUT = c("#545454")
DASHBOARD_WHITE = c("#F2F3ED")
DASHBOARD_MILK = c("#E0CCB8")
DASHBOARD_FULL = Color.from_hex("#9CE256")
DASHBOARD_MID = Color.from_hex("#E2BB56")
DASHBOARD_EMPTY = Color.from_hex("#E28856")


def dashboard_bar_color(v: float = 0.0):
    if v > 0.5:
        return DASHBOARD_FULL.mix(DASHBOARD_MID, 3 * (v - 0.5))
    else:
        return DASHBOARD_EMPTY.mix(DASHBOARD_MID, 3 * (0.5 - v))


class DASHBOARD_FONTS:
    NAME = dict(
        font_name=FONT,
        font_size=18,
        bold=True,
        color=DASHBOARD_WHITE,
        anchor_x="left",
        anchor_y="top",
    )
    TEXT = dict(
        font_name=FONT,
        font_size=14,
        bold=True,
        anchor_x="left",
        anchor_y="top",
    )
    LABEL = dict(
        font_name=FONT,
        font_size=14,
        bold=True,
        color=DASHBOARD_MILK,
        anchor_x="left",
        anchor_y="top",
    )
