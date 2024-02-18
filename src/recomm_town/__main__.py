#!/usr/bin/env python3
from itertools import chain, product
from functools import partial
from random import choice, randint, random

from recomm_town.common import Book, Trivia, Vec
from recomm_town.draw import Draw
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


vowels = "eiuoa"
consonants = "tpsdhjklmn"
syllabes = [c + v for c, v in product(consonants, vowels)]


def make_name() -> str:
    length = randint(2, 4)
    return "".join(choice(syllabes) for _ in range(length)).title()


def make_world():
    skill_trivias = [
        Trivia("skill", "pottery"),
        Trivia("skill", "soldering"),
        Trivia("skill", "crocheting"),
    ]
    paint_trivias = [
        Trivia("paiting", "graffiti"),
        Trivia("paiting", "cubism"),
        Trivia("paiting", "watercolor"),
    ]
    music_trivias = [
        Trivia("music", "techno"),
        Trivia("music", "rock"),
        Trivia("music", "classic"),
    ]
    book_trivias = [
        Trivia("book", "Lem - Solaris"),
        Trivia("book", "Dukaj - Starość aksolotla"),
        Trivia("book", "Tokarczuk - Księgi Jakubowe"),
        Trivia("book", "Lem - Eden"),
        Trivia("book", "Mrożek - Tango"),
        Trivia("book", "Mrożek - Policja"),
        Trivia("book", "Piskorski - 40 i 4")
    ]
    books = [Book(t) for t in book_trivias]

    make_home = partial(
        Place, function=PF.HOME, rooms=list(make_flat_rooms(4, 2)), room_size=120.0
    )
    home_center = Vec(-1000.0, -2000.0)
    home_center_left = home_center + Vec(-800.0, 0.0)
    houses_left = [
        make_home("Flat Andrzej", home_center_left + Vec(0.0, -500.0)),
        make_home("Flat Bogdan", home_center_left + Vec(0.0, +500.0)),
    ]
    home_center_right = home_center + Vec(+800.0, 0.0)
    houses_right = [
        make_home("Flat Czesiek", home_center_right + Vec(0.0, -500.0)),
        make_home("Flat Dawid", home_center_right + Vec(0.0, +500.0)),
    ]

    work = Place(
        "Work",
        Vec(-1000.0, +1000.0),
        PF.WORK,
        make_flat_rooms(8, 4),
        trivias=skill_trivias,
    )
    shop_a = Place("Shop Agata", Vec(0, -300.0), PF.SHOP, make_flat_rooms(2, 2), books=books)
    shop_b = Place("Shop Basia", Vec(+1000.0, -1500.0), PF.SHOP, make_flat_rooms(4, 2))
    garden = Place(
        "Garden",
        Vec(+1000.0, +2000.0),
        PF.ENTERTAIMENT,
        make_grid_rooms(3),
        100.0,
        80.0,
        trivias=music_trivias,
    )
    museum = Place(
        "City museum",
        Vec(0.0, +500.0),
        PF.ENTERTAIMENT,
        make_grid_rooms(2),
        50.0,
        80.0,
        trivias=paint_trivias,
    )

    cross_a = Place("Apple crossway", Vec(-1000.0, 0.0), PF.CROSSROAD)
    cross_b = Place("Cherry crossway", Vec(+1000.0, 0.0), PF.CROSSROAD)
    cross_main = Place("Center", Vec(0.0, 0.0), PF.CROSSROAD)
    cross_home = Place("Coconut crossway", home_center, PF.CROSSROAD)
    cross_home_left = Place("Pinata crossway", home_center_left, PF.CROSSROAD)
    cross_home_right = Place("Banana crossway", home_center_right, PF.CROSSROAD)

    cross_a.connect(cross_home, work)
    cross_b.connect(shop_b, garden)
    cross_main.connect(cross_a, cross_b, museum, shop_a)
    cross_home.connect(cross_home_left, cross_home_right)
    cross_home_left.connect(*houses_left)
    cross_home_right.connect(*houses_right)

    people = []
    houses = houses_left + houses_right
    for home in houses:
        for room in home.rooms:
            info = HumanInfo(
                name=make_name(),
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
            if random() > 0.95:
                human.library.append(choice(books))
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
            cross_home_right,
            cross_home_left,
        ]
    )
    return World(town, people, skill_trivias + paint_trivias + music_trivias + book_trivias)


if __name__ == "__main__":
    world = make_world()

    app = App(world)
    draw = Draw(app.batch, app.people_group)
    draw.draw_gui(len(world.people), app.gui_group)
    draw.draw_path(world.town.path, app.town_group)
    draw.draw_places(world.town.places, app.town_group)
    draw.draw_people(app, world.people, app.people_group)
    app.run()
