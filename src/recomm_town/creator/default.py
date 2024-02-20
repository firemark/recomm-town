from recomm_town.common import Book, Trivia, Vec
from recomm_town.creator.trivias import TriviaBuilder
from recomm_town.town.town import Town
from recomm_town.town.place import Place, PlaceFunction as PF
from recomm_town.world import World

from recomm_town.creator.helpers import (
    CommonBuilder,
    CommonListBuilder,
    make_flat_rooms,
    make_grid_rooms,
    generate_people,
)


class JobBuilder(CommonBuilder[Place]):

    def __init__(self, trivias: TriviaBuilder):
        super().__init__(
            {
                "factory": Place(
                    "Ceramic factory",
                    Vec(-1000.0, +1000.0),
                    PF.WORK,
                    make_flat_rooms(5, 4),
                    trivias=trivias.ceramic,
                ),
                "website_office": Place(
                    "Website office",
                    Vec(+2300.0, +2000.0),
                    PF.WORK,
                    make_flat_rooms(3, 3),
                    trivias=trivias.website,
                ),
                "programming_office": Place(
                    "Blip blob office",
                    Vec(+1000.0, +3000.0),
                    PF.WORK,
                    make_flat_rooms(3, 3),
                    trivias=trivias.programming,
                ),
            }
        )


class HousesBuilder(CommonListBuilder[Place]):

    def __init__(self) -> None:
        self.center = Vec(-1000.0, -2000.0)
        self.center_left = self.center + Vec(-800.0, 0.0)
        self.center_right = self.center + Vec(+800.0, 0.0)

        super().__init__(
            {
                "left": [
                    self._make("Flat Andrzej", self.center_left + Vec(0.0, -500.0)),
                    self._make("Flat Bogdan", self.center_left + Vec(0.0, +500.0)),
                ],
                "right": [
                    self._make("Flat Czesiek", self.center_right + Vec(0.0, -500.0)),
                    self._make("Flat Dawid", self.center_right + Vec(0.0, +500.0)),
                ],
            }
        )

    def _make(self, name: str, position: Vec):
        return Place(
            name=name,
            position=position,
            function=PF.HOME,
            rooms=make_flat_rooms(4, 2),
            room_size=120.0,
        )


class CrossBuilder(CommonBuilder[Place]):

    def __init__(self, home: HousesBuilder):
        super().__init__(
            {
                "a": self._make("Apple", Vec(-1000.0, 0.0)),
                "b": self._make("Cherry", Vec(+1000.0, 0.0)),
                "main": self._make("Center", Vec(0.0, 0.0)),
                "home": self._make("Coconut", home.center),
                "home_left": self._make("Pinata", home.center_left),
                "home_right": self._make("Banana", home.center_right),
            }
        )

    def _make(self, name: str, position: Vec):
        return Place(f"{name} crossway", position, PF.CROSSROAD)


class ShopBuilder(CommonBuilder[Place]):

    def __init__(self, books: list[Book]):
        super().__init__(
            {
                "agata": Place(
                    "Shop Agata",
                    Vec(0, -300.0),
                    PF.SHOP,
                    make_flat_rooms(2, 2),
                    books=books,
                ),
                "basia": Place(
                    "Shop Basia",
                    Vec(+1000.0, -1500.0),
                    PF.SHOP,
                    make_flat_rooms(4, 2),
                    books=books,
                ),
            }
        )


def make_world():
    trivias = TriviaBuilder()
    books = [Book(t) for t in trivias.book + trivias.programming]
    home = HousesBuilder()
    jobs = JobBuilder(trivias)
    cross = CrossBuilder(home)
    shop = ShopBuilder(books)

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

    cross.a.connect(cross.home, jobs.factory)
    cross.b.connect(shop.basia, garden)
    cross.main.connect(cross.a, cross.b, museum, shop.agata)
    cross.home.connect(cross.home_left, cross.home_right)
    cross.home_left.connect(*home.left)
    cross.home_right.connect(*home.right)
    garden.connect(jobs.programming_office, jobs.website_office)

    houses = list(home)
    people = generate_people(houses, jobs, books)

    town = Town(
        [
            *houses,
            *jobs,
            *cross,
            *shop,
            garden,
            museum,
        ]
    )
    return World(town, people, list(trivias))
