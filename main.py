#!/usr/bin/env python3
from itertools import chain
from functools import partial

from pyglet.shapes import Line, Rectangle, Circle
from pyglet.text import Label

from src.common import Vec
from src.town.town import Town
from src.town.place import LocalRoom, Place, PlaceFunction as PF
from src.human import Human
from src.world import World
from src.app import App


def make_flat_rooms(n, m):
    return chain.from_iterable(
        [
            LocalRoom(Vec(-x, +y)),
            LocalRoom(Vec(+x, +y)),
        ]
        for x in range(1, n + 1)
        for y in range(-1, m * 2 - 1, 2)
    )


def make_grid_rooms(n):
    return chain.from_iterable(
        [
            LocalRoom(Vec(-x, -y)),
            LocalRoom(Vec(-x, +y)),
            LocalRoom(Vec(+x, +y)),
            LocalRoom(Vec(+x, -y)),
        ]
        for x in range(1, n + 1)
        for y in range(1, n + 1)
    )


def make_world():
    few_rooms = [
        LocalRoom(Vec(-1.0, -1.0)),
        LocalRoom(Vec(+1.0, -1.0)),
        LocalRoom(Vec(+1.0, +1.0)),
        LocalRoom(Vec(-1.0, +1.0)),
    ]

    home = Place("Home", Vec(-1000.0, -1000.0), PF.HOME, make_flat_rooms(8, 2))
    work = Place("Work", Vec(-1000.0, +1000.0), PF.WORK, make_flat_rooms(8, 4))
    shop = Place("Shop", Vec(+1000.0, -1000.0), PF.SHOP, make_flat_rooms(4, 2))
    museum = Place(
        "Museum", Vec(+1000.0, +1000.0), PF.MUSEUM, make_grid_rooms(3), 100.0, 50.0
    )

    cross_a = Place("Apple crossway", Vec(-1000.0, 0.0), PF.CROSSROAD)
    cross_b = Place("Cherry crossway", Vec(+1000.0, 0.0), PF.CROSSROAD)
    cross_main = Place("Center", Vec(0.0, 0.0), PF.CROSSROAD)

    cross_a.connect(home, work)
    cross_b.connect(shop, museum)
    cross_main.connect(cross_a, cross_b)

    human_a = Human(home.position, speed=3.0)
    human_b = Human(work.position, speed=1.8)
    human_c = Human(home.position, speed=2.2)

    town = Town([home, work, shop, museum, cross_a, cross_b, cross_main])
    return World(town, [human_a, human_b, human_c])


if __name__ == "__main__":
    RED = (0xFF, 0x00, 0x00)
    BLUE = (0x00, 0x00, 0xFF)
    GREEN = (0x00, 0xFF, 0x00)
    BLACK = (0x00, 0x00, 0x00)
    WHITE = (0xFF, 0xFF, 0xFF)
    GREY = (0xAA, 0xAA, 0xAA)

    world = make_world()
    from pprint import pprint

    pprint(world.town.path)
    app = App(world)
    objs = []

    kw = dict(batch=app.batch, group=app.town_group)
    kw_font = dict(
        font_name="Monospace",
        anchor_x="center",
        anchor_y="center",
        color=(0, 0, 0, 255),
        **kw
    )

    for way in world.town.path:
        a = way.a.position
        b = way.b.position
        objs.append(Line(a.x, a.y, b.x, b.y, width=50.0, color=RED, **kw))

    for place in world.town.places:
        color = GREEN if place.function == PF.CROSSROAD else GREY
        p = place.position
        start = place.box_start
        size = place.box_end - start
        title = place.function.name.title()

        objs.append(Rectangle(start.x, start.y, size.x, size.y, color=color, **kw))
        objs.append(Label(title, x=p.x, y=p.y, font_size=36, **kw_font))
        objs.append(
            Label(place.name, x=p.x, y=p.y + size.y - 12, font_size=48, **kw_font)
        )

        s = place.room_size
        h = s / 2
        for room in place.rooms:
            r = room.position - h
            objs.append(Rectangle(r.x, r.y, s, s, color=BLUE, **kw))

    def update(sprite, v):
        sprite.x = v.x
        sprite.y = v.y

    kw = dict(batch=app.batch, group=app.people_group)
    for human in world.people:
        p = human.position
        sprite = Circle(p.x, p.y, 20, color=WHITE, **kw)
        human.position_observers.append(partial(update, sprite))
        objs.append(sprite)

    app.run()
