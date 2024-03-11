from dataclasses import dataclass
import os
import platform
from pathlib import Path

from recomm_town.common import Color
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
    l_skin = Color.from_hex("#E0CCB8")
    d_skin = Color.from_hex("#362617")
    white = Color.from_hex("#FFFFFF")


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
class PlaceColors:
    room_texture_id: int = 0
    textures_len: int = 1
    place_color_bg: tuple[int, int, int, int] = PALLETE.road.to_pyglet_alpha()
    icon_size: float = 1.0
    icon_color_r: tuple[int, int, int, int] = n()
    icon_color_g: tuple[int, int, int, int] = n()
    icon_color_b: tuple[int, int, int, int] = n()
    room_color_bg: tuple[int, int, int, int] = n()

PLACE_COLORS = {
    "default": PlaceColors(),
    "garden": PlaceColors(
        room_texture_id=1,
        textures_len=2,
        place_color_bg=PALLETE.road.to_pyglet_alpha(),
        icon_color_r=PALLETE.d_grass.to_pyglet_alpha(),
        icon_color_g=PALLETE.l_grass.to_pyglet_alpha(),
    ),
    "museum": PlaceColors(
        room_texture_id=2,
        icon_size=0.6,
        place_color_bg=c("#D0BDE3"),
        icon_color_g=c("#D686D4"),
        icon_color_b=c("#CE6EC8"),
        room_color_bg=c("#7A58A0"),
    ),
    "pub": PlaceColors(
        room_texture_id=3,
        textures_len=2,
        icon_size=0.6,
        place_color_bg=c("#EFE4C8"),
        icon_color_r=c("#D68663"),
        icon_color_g=c("#FDC362"),
        icon_color_b=c("#FFD199"),
        room_color_bg=c("#ECA756"),
    ),
    "work": PlaceColors(
        place_color_bg=PALLETE.l_grey.to_pyglet_alpha(),
        room_color_bg=PALLETE.d_grey.to_pyglet_alpha(),
    ),
    "home": PlaceColors(
        room_texture_id=4,
        textures_len=1,
        place_color_bg=PALLETE.i_blue.to_pyglet_alpha(),
        room_color_bg=PALLETE.l_blue.to_pyglet_alpha(),
        icon_color_r=c("#DAF4FF"),
        icon_color_g=c("#3F768C"),
        icon_color_b=c("#F2F3ED"),
    ),
    "shop": PlaceColors(
        place_color_bg=PALLETE.i_purple.to_pyglet_alpha(),
        room_color_bg=PALLETE.l_purple.to_pyglet_alpha(),
    ),
    "entertainment": PlaceColors(
        place_color_bg=PALLETE.l_blue.to_pyglet_alpha(),
        room_color_bg=PALLETE.d_blue.to_pyglet_alpha(),
    ),
    "community": PlaceColors(
        room_texture_id=2,
        place_color_bg=PALLETE.l_blue.to_pyglet_alpha(),
        room_color_bg=PALLETE.d_blue.to_pyglet_alpha(),
    ),
}

LEVELS = ["fridge", "satiety", "money", "energy"]
LEVEL_COLORS = {
    "fridge": to_color("#D9DAD2"),
    "satiety": to_color("#01A638"),
    "money": to_color("#F1D651"),
    "energy": to_color("#FF5349"),
}

ACTIVITY_LIGHT_COLORS = {
    Activity.NONE: n(),
    Activity.MOVE: PALLETE.l_red.to_pyglet_alpha(),
    Activity.WORK: PALLETE.d_grey.to_pyglet_alpha(),
    Activity.SHOP: PALLETE.d_grey.to_pyglet_alpha(),
    Activity.TALK: PALLETE.d_blue.to_pyglet_alpha(),
    Activity.READ: PALLETE.l_yellow.to_pyglet_alpha(),
    Activity.RADIO: PALLETE.l_yellow.to_pyglet_alpha(),
    Activity.TV: PALLETE.l_yellow.to_pyglet_alpha(),
    Activity.WTF: PALLETE.l_red.to_pyglet_alpha(),
    Activity.EAT: PALLETE.l_green.to_pyglet_alpha(),
    Activity.SLEEP: PALLETE.l_blue.to_pyglet_alpha(),
    Activity.TIME_BREAK: PALLETE.white.to_pyglet_alpha(),
    Activity.ENJOY: PALLETE.l_blue.to_pyglet_alpha(),
    Activity.SHARE: PALLETE.l_red.to_pyglet_alpha(),
    Activity.IDEA: PALLETE.l_purple.to_pyglet_alpha(),
}

ACTIVITY_DARK_COLORS = ACTIVITY_LIGHT_COLORS.copy()
ACTIVITY_DARK_COLORS |= {
    Activity.SLEEP: PALLETE.l_blue.to_pyglet_alpha(),
    Activity.EAT: PALLETE.i_green.to_pyglet_alpha(),
    Activity.WORK: PALLETE.white.to_pyglet_alpha(),
    Activity.SHOP: PALLETE.white.to_pyglet_alpha(),
    Activity.TALK: PALLETE.i_blue.to_pyglet_alpha(),
}

# ACTIVITY_COLORS = {
#     Activity.NONE: (n(), n(), n()),
#     Activity.MOVE: (c("#E30B5C"), n(), n()),
#     Activity.WORK: (c("#8B8680"), n(), n()),
#     Activity.SHOP: (c("#C9C0BB"), c("#00000044"), n()),
#     Activity.TALK: (c("#0095B7"), c("#FFFFFF"), c("#000000")),
#     Activity.READ: (c("#AF593E"), c("#CA3435"), c("#2D383A")),
#     Activity.RADIO: (c("#805533"), c("#C9C0BB"), c("#736A62")),
#     Activity.TV: (c("#665233"), c("#C9C0BB"), c("#FFFFFF")),
#     Activity.WTF: (c("#FF0000"), n(), n()),
#     Activity.EAT: (c("#87421F"), c("#CA3435"), c("#FFFFFF")),
#     Activity.SLEEP: (c("#0066CC"), c("#000000"), n()),
#     Activity.TIME_BREAK: (c("#FFFFFF"), c("#FFFF66"), c("#00000044")),
#     Activity.ENJOY: (c("#02A4D3"), c("#87421F"), c("#FFFFFF")),
#     Activity.SHARE: (c("#D92121"), c("#FFFFFF"), c("#000000")),
#     Activity.IDEA: (c("#D92121"), c("#FFFFFF"), c("#000000")),
# }


ACTIVITY_TEXTURE_VARIANTS = {
    Activity.NONE: 1,
    Activity.MOVE: 1,
    Activity.WORK: 1,
    Activity.SHOP: 1,
    Activity.TALK: 1,
    Activity.READ: 1,
    Activity.RADIO: 1,
    Activity.TV: 1,
    Activity.WTF: 3,
    Activity.EAT: 3,
    Activity.SLEEP: 1,
    Activity.TIME_BREAK: 1,
    Activity.SHARE: 1,
    Activity.ENJOY: 2,
    Activity.IDEA: 1,
}

ACTIVITY_LABELS = {
    Activity.NONE: "-",
    Activity.MOVE: "Moving",
    Activity.WORK: "Working",
    Activity.SHOP: "Shopping",
    Activity.TALK: "Seeking to talk",
    Activity.READ: "Reading a book",
    Activity.RADIO: "Listening a radio",
    Activity.TV: "Watching a TV channel",
    Activity.WTF: "Little a bit confusing",
    Activity.EAT: "Eating",
    Activity.SLEEP: "Sleeping",
    Activity.TIME_BREAK: "Waiting",
    Activity.ENJOY: "Enjoy",
    Activity.SHARE: "Talking & Sharing",
    Activity.IDEA: "Gatherind ideas",
}