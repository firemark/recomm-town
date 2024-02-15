from functools import partial

from pyglet.graphics import Batch, Group
from pyglet.shapes import Line, Rectangle, Circle
from pyglet.text import Label
from recomm_town.human.human import Human

from recomm_town.town import PlaceFunction as PF
from recomm_town.town.place import Place, Way


class COLORS:
    room = (0x00, 0x00, 0xFF)
    human = (0xFF, 0xFF, 0xFF)
    place = (0xAA, 0xAA, 0xAA)
    crossroad = (0x00, 0xFF, 0x00)
    way = (0xFF, 0x00, 0x00)


class Draw:
    def __init__(self, batch: Batch) -> None:
        self.objs = []
        self.kw = dict(batch=batch)
        self.kw_font = dict(
            font_name="Monospace",
            anchor_x="center",
            anchor_y="center",
            color=(0, 0, 0, 255),
            **self.kw,
        )

    def draw_path(self, path: list[Way], group: Group):
        kw = dict(**self.kw, group=group, width=50.0, color=COLORS.way)
        for way in path:
            a = way.a.position
            b = way.b.position
            self.objs.append(Line(a.x, a.y, b.x, b.y, **kw))

    def draw_places(self, places: list[Place], group: Group):
        kw = dict(**self.kw, group=group)

        for place in places:
            color = COLORS.crossroad if place.function == PF.CROSSROAD else COLORS.place
            p = place.position
            start = place.box_start
            size = place.box_end - start

            self.objs += [
                Rectangle(start.x, start.y, size.x, size.y, color=color, **kw),
                Label(place.name, x=p.x, y=p.y, font_size=36, **self.kw_font),
            ]

            s = place.room_size
            h = s / 2
            for room in place.rooms:
                r = room.position - h
                self.objs.append(Rectangle(r.x, r.y, s, s, color=COLORS.room, **kw))

    def draw_people(self, people: list[Human], group: Group):
        kw = dict(**self.kw, group=group)
        update = self.update_human_position
        for human in people:
            p = human.position
            sprite = Circle(p.x, p.y, 20, color=COLORS.human, **kw)
            human.position_observers.append(partial(update, sprite))
            self.objs.append(sprite)

    @staticmethod
    def update_human_position(sprite, human, _):
        sprite.x = human.position.x
        sprite.y = human.position.y
