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
                    Vec(-2000.0, +1000.0),
                    PF.WORK,
                    make_flat_rooms(5, 5),
                    trivias=trivias.ceramic,
                ),
                "office": Place(
                    "Happy cats office",
                    Vec(+2000.0, +1000.0),
                    PF.WORK,
                    make_flat_rooms(5, 5),
                    trivias=trivias.website,
                ),
            }
        )


class HousesBuilder(CommonListBuilder[Place]):

    def __init__(self) -> None:
        self.cross_l = Vec(-2000.0, -2000.0)
        self.cross_r = Vec(+2000.0, -2000.0)
        self.cross_ll = self.cross_l + Vec(-1000.0, 0.0)
        self.cross_lr = self.cross_l + Vec(+1000.0, 0.0)
        self.cross_rl = self.cross_r + Vec(-1000.0, 0.0)
        self.cross_rr = self.cross_r + Vec(+1000.0, 0.0)

        super().__init__(
            {
                "ll": self._make_diagonal(
                    ["Müller", "Becker", "Karl", "Fischer"],
                    self.cross_ll,
                ),
                "lr": self._make_diagonal(
                    ["Schmidt", "Schulz", "Jonas", "Weber"],
                    self.cross_lr,
                ),
                "rl": self._make_diagonal(
                    ["Schneider", "Finn", "Noah", "Meyer"],
                    self.cross_rl,
                ),
                "rr": self._make_diagonal(
                    ["Hoffman", "Lukas", "Frederick", "Wagner"],
                    self.cross_rr,
                ),
            }
        )

    def _make_diagonal(self, names: list[str], center: Vec) -> list[Place]:
        d = 400.0
        return [
            self._make(names[0], center + Vec(+d, +d), 45 + 90 + 180),
            self._make(names[1], center + Vec(-d, +d), 45),
            self._make(names[2], center + Vec(-d, -d), 45 + 90),
            self._make(names[3], center + Vec(+d, -d), 45 + 180),
        ]

    def _make(self, name: str, position: Vec, rotation: float):
        return Place(
            name=name,
            position=position,
            function=PF.HOME,
            rooms=make_flat_rooms(1, 3),
            room_size=120.0,
            rotation=rotation,
        )


class CrossBuilder(CommonBuilder[Place]):

    def __init__(self, home: HousesBuilder):
        super().__init__(
            {
                "left": self._make("Abelia", Vec(-2000.0, 0.0)),
                "right": self._make("Begonia", Vec(+2000.0, 0.0)),
                "center": self._make("Cactus", Vec(0.0, 0.0)),
                "shop": self._make("Yarrow", Vec(0.0, -500.0)),
                "home_l": self._make("Daffodil", home.cross_l),
                "home_ll": self._make("Gasteria", home.cross_ll),
                "home_lr": self._make("Palm", home.cross_lr),
                "home_r": self._make("Dahlia", home.cross_r),
                "home_rl": self._make("Geraniums", home.cross_rl),
                "home_rr": self._make("Magnolia", home.cross_rr),
            }
        )

    def _make(self, name: str, position: Vec):
        return Place(f"{name} crossway", position, PF.CROSSROAD)


class ShopBuilder(CommonBuilder[Place]):

    def __init__(self, books: list[Book]):
        super().__init__(
            {
                "anastazja": Place(
                    "Shop Anastazja",
                    Vec(-500.0, -500.0),
                    PF.SHOP,
                    make_flat_rooms(4, 2),
                    books=books,
                    rotation=90,
                ),
                "emeralda": Place(
                    "Shop Emeralda",
                    Vec(+500.0, -500.0),
                    PF.SHOP,
                    make_flat_rooms(4, 2),
                    books=books,
                    rotation=90,
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
        Vec(+0.0, +1000.0),
        PF.ENTERTAIMENT,
        make_grid_rooms(4),
        100.0,
        80.0,
        trivias=trivias.paint,
    )

    cross.left.connect(cross.home_l, jobs.factory)
    cross.right.connect(cross.home_r, jobs.office)
    cross.center.connect(cross.left, cross.right, cross.shop, garden)
    cross.shop.connect(shop.anastazja, shop.emeralda)
    cross.home_l.connect(cross.home_ll, cross.home_lr)
    cross.home_r.connect(cross.home_rl, cross.home_rr)
    cross.home_ll.connect(*home.ll)
    cross.home_lr.connect(*home.lr)
    cross.home_rl.connect(*home.rl)
    cross.home_rr.connect(*home.rr)

    houses_l = home.ll + home.lr
    houses_r = home.rl + home.rr
    people_l = generate_people(houses_l, [jobs.factory], books)
    people_r = generate_people(houses_r, [jobs.office], books)

    town = Town(
        [
            *home,
            *jobs,
            *cross,
            *shop,
            garden,
        ]
    )
    return World(
        town, people_l + people_r, radio_program=trivias.music, tv_program=trivias.tv
    )
