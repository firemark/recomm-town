from collections import defaultdict
from random import randint, random

from pyglet.graphics import Batch, Group
from pyglet.image import ImageGrid, load as image_load
from pyglet.shapes import Line, Rectangle, BorderedRectangle
from pyglet.window import Window
from pyglet.text import Label

from recomm_town.app import GuiGroup
from recomm_town.shaders import AnimatedLine, Sprite
from recomm_town.shaders.human_group import HumanGroup
from recomm_town.common import Color, Trivia, TriviaChunk, Vec
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


def _crop_label(label: str, size: int) -> str:
    if len(label) <= size:
        return label
    else:
        return label[: size - 1] + "…"


class COLORS:
    dashboard_text = Color.from_hex("#FFFFFF")
    dashboard_bg = Color.from_hex("#000000")
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


LEVELS = ["fridge", "satiety", "money", "energy"]
LEVEL_COLORS = {
    "fridge": _to_color("#D9DAD2"),
    "satiety": _to_color("#01A638"),
    "money": _to_color("#F1D651"),
    "energy": _to_color("#FF5349"),
}

ACTIVITY_COLORS = {
    Activity.NONE: (_n(), _n(), _n()),
    Activity.MOVE: (_c("#E30B5C"), _n(), _n()),
    Activity.WORK: (_c("#8B8680"), _n(), _n()),
    Activity.SHOP: (_c("#C9C0BB"), _c("#00000044"), _n()),
    Activity.TALK: (_c("#0095B7"), _c("#FFFFFF"), _c("#000000")),
    Activity.READ: (_c("#AF593E"), _c("#CA3435"), _c("#2D383A")),
    Activity.RADIO: (_c("#805533"), _c("#C9C0BB"), _c("#736A62")),
    Activity.TV: (_c("#665233"), _c("#C9C0BB"), _c("#FFFFFF")),
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
    Activity.TIME_BREAK: "Relaxing",
    Activity.ENJOY_DRINK: "Enjoy",
    Activity.ENJOY_PLAY: "Enjoy",
    Activity.ENJOY_MUSIC: "Enjoy",
    Activity.SHARE_LOVE: "Talking & Sharing",
    Activity.SHARE_MUSIC: "Talking & Sharing",
    Activity.SHARE_WOW: "Talking & Sharing",
}


class Draw:
    def __init__(self, batch: Batch, people_group: Group, gui_group: GuiGroup) -> None:
        self.objs = []
        self.batch = batch
        self.gui_group = gui_group
        self.kw = dict(batch=batch)
        self.kw_font = dict(
            font_name="Monospace",
            anchor_x="center",
            anchor_y="center",
            **self.kw,
        )
        self.people_group = people_group
        self.trivias_level = defaultdict(float)
        self.activity_sprites = ImageGrid(image_load("textures/activities.png"), 4, 5)
        self.human_sprites = ImageGrid(image_load("textures/human.png"), 2, 2)
        self.learnbar_image = image_load("textures/learnbar.png")
        self.tracked_human: TrackHumanDraw | None = None
        self.lifeobjs = {}

    def draw_gui(self, people_count):
        kw = dict(**self.kw, group=self.gui_group)
        kw_font = dict(
            **kw,
            color=COLORS.dashboard_text.to_pyglet_alpha(),
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
                color=COLORS.dashboard_bg.to_pyglet_alpha(0.5),
                border_color=COLORS.dashboard_text.to_pyglet(),
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
            center = p - place.box_start
            start = center + place.box_start

            rect = Rectangle(start.x, start.y, size.x, size.y, color=color, **kw)
            rect.anchor_position = center
            rect.rotation = -rot

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
                rect.rotation = -rot
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

    def track_human(self, human: Human | None):
        if self.tracked_human is not None:
            self.tracked_human.stop()
        if human is None:
            return
        self.tracked_human = TrackHumanDraw(human, self.batch, self.gui_group)

    def _trivia_update(self, trivia_chunk, new, old):
        diff = new - old
        if diff == 0.0:
            return
        trivia, chunk_id = trivia_chunk
        self.trivias_level[trivia] += diff / trivia.chunks
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
        return f"{i:2}. {_crop_label(name, size=40):40} {percent:6.2f} %"

    def _talk_update(self, a: Human, b: Human, trivia: Trivia | None, state: str):
        kw = dict(**self.kw, group=self.people_group)
        kw_font = dict(
            **self.kw_font,
            font_size=18,
            bold=True,
            color=(0x00, 0x22, 0x55, 0xFF),
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


class TrackHumanDraw:
    def __init__(self, human: Human, batch: Batch, group: GuiGroup):
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
            font_name="Monospace",
            font_size=14,
            bold=True,
            anchor_x="left",
            anchor_y="top",
        )

        df_color = COLORS.dashboard_text.to_pyglet_alpha()
        x = 1000.0
        y = -300.0
        self.objs = {
            "background": BorderedRectangle(
                x=x,
                y=y,
                width=850.0,
                height=300.0,
                border=10,
                color=COLORS.dashboard_bg.to_pyglet_alpha(0.5),
                border_color=COLORS.dashboard_text.to_pyglet(),
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
            f"{index}. {_crop_label(trivia.name, size=25):25} "
            f"{level / trivia.chunks * 100:3.0f} %"
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
