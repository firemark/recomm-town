#!/usr/bin/env python3
from functools import partial

from pyglet.shapes import Line, Rectangle, Circle
from pyglet.text import Label

from src.common import Vec
from src.town.town import Town
from src.town.place import Place, PlaceFunction as PF
from src.actions import Move
from src.human import Human
from src.world import World
from src.app import App


def make_world():
    home = Place("Home", Vec(-1000.0, -1000.0), PF.HOME)
    work = Place("Work", Vec(-1000.0, +1000.0), PF.WORK)
    shop = Place("Shop", Vec(+1000.0, -1000.0), PF.SHOP)
    museum = Place("Museum", Vec(+1000.0, +1000.0), PF.MUSEUM)

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
        color = GREEN if place.function == PF.CROSSROAD else BLUE
        p = place.position
        s = 100.0 if place.function == PF.CROSSROAD else 200.0
        objs.append(Rectangle(p.x - s / 2, p.y - s / 2, s, s, color=color, **kw))
        objs.append(
            Label(place.function.name.title(), x=p.x, y=p.y, font_size=36, **kw_font)
        )
        objs.append(Label(place.name, x=p.x, y=p.y + s - 12, font_size=48, **kw_font))

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
