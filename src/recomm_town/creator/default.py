from recomm_town.common import Book, Trivia, Vec
from recomm_town.town.town import Town
from recomm_town.town.place import Place, PlaceFunction as PF
from recomm_town.world import World

from recomm_town.creator.helpers import (
    make_flat_rooms,
    make_grid_rooms,
    generate_people,
)


class TriviaBuilder:

    def __init__(self):
        self.ceramic = [
            Trivia("skill", "pottery"),
            Trivia("skill", "wine glass"),
            Trivia("skill", "ceramic"),
            Trivia("skill", "stained glass"),
        ]
        self.website = [
            Trivia("skill", "HTML"),
            Trivia("skill", "CSS"),
            Trivia("skill", "GUI"),
        ]
        self.programming = [
            Trivia("skill", "python"),
            Trivia("skill", "javascript"),
            Trivia("skill", "c++"),
        ]
        self.paint = [
            Trivia("paiting", "dada"),
            Trivia("paiting", "cubism"),
            Trivia("paiting", "watercolor"),
            Trivia("paiting", "hypperrealism"),
        ]
        self.music = [
            Trivia("music", "techno"),
            Trivia("music", "rock"),
            Trivia("music", "classic"),
            Trivia("music", "country"),
        ]
        self.book = [
            Trivia("book", "Lem - Solaris"),
            Trivia("book", "Dukaj - Starość aksolotla"),
            Trivia("book", "Tokarczuk - Księgi Jakubowe"),
            Trivia("book", "Lem - Eden"),
            Trivia("book", "Mrożek - Tango"),
            Trivia("book", "Mrożek - Policja"),
            Trivia("book", "Piskorski - 40 i 4"),
        ]

    def __iter__(self):
        yield from self.ceramic
        yield from self.website
        yield from self.programming
        yield from self.paint
        yield from self.music
        yield from self.book


class JobBuilder:

    def __init__(self, trivias: TriviaBuilder):
        self.factory = Place(
            "Ceramic factory",
            Vec(-1000.0, +1000.0),
            PF.WORK,
            make_flat_rooms(5, 4),
            trivias=trivias.ceramic,
        )
        self.website_office = Place(
            "Website office",
            Vec(+2300.0, +2000.0),
            PF.WORK,
            make_flat_rooms(3, 3),
            trivias=trivias.website,
        )
        self.programming_office = Place(
            "Blip blob office",
            Vec(+1000.0, +3000.0),
            PF.WORK,
            make_flat_rooms(3, 3),
            trivias=trivias.programming,
        )

    def __iter__(self):
        yield self.factory
        yield self.website_office
        yield self.programming_office


class HousesBuilder:

    def __init__(self) -> None:
        self.center = Vec(-1000.0, -2000.0)
        self.center_left = self.center + Vec(-800.0, 0.0)
        self.center_right = self.center + Vec(+800.0, 0.0)

        self.houses_left = [
            self._make_home("Flat Andrzej", self.center_left + Vec(0.0, -500.0)),
            self._make_home("Flat Bogdan", self.center_left + Vec(0.0, +500.0)),
        ]
        self.houses_right = [
            self._make_home("Flat Czesiek", self.center_right + Vec(0.0, -500.0)),
            self._make_home("Flat Dawid", self.center_right + Vec(0.0, +500.0)),
        ]

    def _make_home(self, name: str, position):
        return Place(
            name=name,
            position=position,
            function=PF.HOME,
            rooms=make_flat_rooms(4, 2),
            room_size=120.0,
        )

    def __iter__(self):
        yield from self.houses_left
        yield from self.houses_right


def make_world():
    trivias = TriviaBuilder()
    books = [Book(t) for t in trivias.book]
    programming_books = [Book(t) for t in trivias.programming]
    home = HousesBuilder()
    jobs = JobBuilder(trivias)

    shop_a = Place(
        "Shop Agata",
        Vec(0, -300.0),
        PF.SHOP,
        make_flat_rooms(2, 2),
        books=books + programming_books,
    )
    shop_b = Place(
        "Shop Basia",
        Vec(+1000.0, -1500.0),
        PF.SHOP,
        make_flat_rooms(4, 2),
        books=books,
    )
    garden = Place(
        "Garden",
        Vec(+1000.0, +2000.0),
        PF.ENTERTAIMENT,
        make_grid_rooms(3),
        100.0,
        80.0,
        trivias=trivias.paint,
    )
    museum = Place(
        "City museum",
        Vec(0.0, +500.0),
        PF.ENTERTAIMENT,
        make_grid_rooms(2),
        50.0,
        80.0,
        trivias=trivias.music,
    )

    cross_a = Place("Apple crossway", Vec(-1000.0, 0.0), PF.CROSSROAD)
    cross_b = Place("Cherry crossway", Vec(+1000.0, 0.0), PF.CROSSROAD)
    cross_main = Place("Center", Vec(0.0, 0.0), PF.CROSSROAD)
    cross_home = Place("Coconut crossway", home.center, PF.CROSSROAD)
    cross_home_left = Place("Pinata crossway", home.center_left, PF.CROSSROAD)
    cross_home_right = Place("Banana crossway", home.center_right, PF.CROSSROAD)

    cross_a.connect(cross_home, jobs.factory)
    cross_b.connect(shop_b, garden)
    cross_main.connect(cross_a, cross_b, museum, shop_a)
    cross_home.connect(cross_home_left, cross_home_right)
    cross_home_left.connect(*home.houses_left)
    cross_home_right.connect(*home.houses_right)
    garden.connect(jobs.programming_office, jobs.website_office)

    houses = list(home)
    people = generate_people(houses, jobs, books)

    town = Town(
        [
            *houses,
            *jobs,
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
    return World(town, people, list(trivias))
