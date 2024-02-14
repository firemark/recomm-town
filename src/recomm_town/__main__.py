#!/usr/bin/env python3
from itertools import chain
from functools import partial
from math import copysign
from random import choice, random

from pyglet.shapes import Line, Rectangle, Circle
from pyglet.text import Label

from recomm_town.common import Vec
from recomm_town.town.town import Town
from recomm_town.town.place import LocalRoom, Place, PlaceFunction as PF
from recomm_town.human import Human, HumanInfo
from recomm_town.world import World
from recomm_town.app import App


def make_flat_rooms(n, m):
    max_lvl = m * 2 - 4

    for y in range(-1, m * 2 - 1, 2):
        lvl = min(max_lvl, y + 1)
        yield from (
            LocalRoom(Vec(-x, +y), [Vec(0, lvl), Vec(-x, lvl)])
            for x in chain.from_iterable((-x, x) for x in range(+1, n + 1))
        )


def make_grid_rooms(n):
    return (
        LocalRoom(Vec(x, y), [Vec(x + hall, 0), Vec(x + hall, y)])
        for x, y, hall in chain.from_iterable(
            [(-x, -y, +0.5), (-x, +y, +0.5), (+x, +y, -0.5), (+x, -y, -0.5)]
            for x in range(1, n + 1)
            for y in range(1, n + 1)
        )
    )


def make_world():
    make_home = partial(
        Place, function=PF.HOME, rooms=list(make_flat_rooms(4, 2)), room_size=120.0
    )
    home_center = Vec(-1000.0, -2000.0)
    houses = [
        make_home("Home A", home_center + Vec(-800.0, -300.0)),
        make_home("Home B", home_center + Vec(+800.0, -300.0)),
        make_home("Home C", home_center + Vec(+800.0, +300.0)),
        make_home("Home D", home_center + Vec(-800.0, +300.0)),
    ]

    work = Place("Work", Vec(-1000.0, +1000.0), PF.WORK, make_flat_rooms(8, 4))
    shop_a = Place("Shop A", Vec(0, -300.0), PF.SHOP, make_flat_rooms(2, 2))
    shop_b = Place("Shop B", Vec(+1000.0, -1500.0), PF.SHOP, make_flat_rooms(4, 2))
    garden = Place(
        "Garden",
        Vec(+1000.0, +2000.0),
        PF.ENTERTAIMENT,
        make_grid_rooms(3),
        100.0,
        80.0,
    )
    museum = Place(
        "City museum", Vec(0.0, +500.0), PF.ENTERTAIMENT, make_grid_rooms(2), 50.0, 80.0
    )

    cross_a = Place("Apple crossway", Vec(-1000.0, 0.0), PF.CROSSROAD)
    cross_b = Place("Cherry crossway", Vec(+1000.0, 0.0), PF.CROSSROAD)
    cross_main = Place("Center", Vec(0.0, 0.0), PF.CROSSROAD)
    cross_home = Place("Coconut crossway", home_center, PF.CROSSROAD)

    cross_a.connect(cross_home, work)
    cross_b.connect(shop_b, garden)
    # garden.connect(work, museum)
    cross_main.connect(cross_a, cross_b, museum, shop_a)
    cross_home.connect(*houses)

    people = []
    for i in range(4):
        home = houses[i]
        for j in range(4):
            while True:
                room = choice(home.rooms)
                if room.occupied_by:
                    continue
                break
            info = HumanInfo(
                name=f"Person {i}{chr(j + ord('A'))}",
                liveplace=home,
                liveroom=room,
                workplace=work,
                speed=5.0 + random() * 5.0,
            )
            human = Human(info.liveroom.position, info)
            human.levels.money += random()
            human.levels.tiredness += random() * 0.5
            human.levels.fullness -= random() * 0.3
            human.levels.fridge -= random() * 0.5
            room.occupied_by = human
            people.append(human)

    town = Town(
        houses
        + [
            work,
            shop_a,
            shop_b,
            garden,
            museum,
            cross_home,
            cross_a,
            cross_b,
            cross_main,
        ]
    )
    return World(town, people)


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
        **kw,
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

        objs.append(Rectangle(start.x, start.y, size.x, size.y, color=color, **kw))
        objs.append(Label(place.name, x=p.x, y=p.y, font_size=36, **kw_font))
        # objs.append(
        #     Label(place.name, x=p.x, y=p.y + size.y - 12, font_size=48, **kw_font)
        # )

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
