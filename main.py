#!/usr/bin/env python3
from pyglet.shapes import Line, Rectangle
from pyglet.text import Label

from src.common import Vec
from src.town import Town, Place, PlaceFunction as PF
from src.app import App


def make_town():
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

    return Town({home, work, shop, museum, cross_a, cross_b, cross_main})


if __name__ == "__main__":
    RED = (0xFF, 0x00, 0x00)
    BLUE = (0x00, 0x00, 0xFF)
    GREEN = (0x00, 0xFF, 0x00)
    BLACK = (0x00, 0x00, 0x00)
    town = make_town()
    from pprint import pprint

    pprint(town.path)
    app = App()
    objs = []

    kw = dict(batch=app.batch, group=app.town_group)
    kw_font = dict(
        font_name="Monospace",
        anchor_x="center",
        anchor_y="center",
        color=(0, 0, 0, 255),
        **kw
    )

    for way in town.path:
        a = way.a.position
        b = way.b.position
        objs.append(Line(a.x, a.y, b.x, b.y, width=50.0, color=RED, **kw))

    for place in town.places:
        color = GREEN if place.function == PF.CROSSROAD else BLUE
        p = place.position
        s = 100.0 if place.function == PF.CROSSROAD else 200.0
        objs.append(Rectangle(p.x - s / 2, p.y - s / 2, s, s, color=color, **kw))
        objs.append(
            Label(place.function.name.title(), x=p.x, y=p.y, font_size=36, **kw_font)
        )
        objs.append(Label(place.name, x=p.x, y=p.y + s - 12, font_size=48, **kw_font))

    app.run()
