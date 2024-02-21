from recomm_town.common import Trivia
from recomm_town.creator.helpers import CommonListBuilder


class TriviaBuilder(CommonListBuilder[Trivia]):

    def __init__(self):
        super().__init__(
            {
                "ceramic": [
                    Trivia("skill", "pottery"),
                    Trivia("skill", "wine glass"),
                    Trivia("skill", "ceramic"),
                    Trivia("skill", "stained glass"),
                ],
                "website": [
                    Trivia("skill", "HTML"),
                    Trivia("skill", "CSS"),
                    Trivia("skill", "GUI"),
                ],
                "programming": [
                    Trivia("skill", "python"),
                    Trivia("skill", "javascript"),
                    Trivia("skill", "c++"),
                ],
                "paint": [
                    Trivia("paiting", "dada"),
                    Trivia("paiting", "cubism"),
                    Trivia("paiting", "watercolor"),
                    Trivia("paiting", "hypperrealism"),
                ],
                "music": [
                    Trivia("music", "techno"),
                    Trivia("music", "rock"),
                    Trivia("music", "classic"),
                    Trivia("music", "country"),
                ],
                "book": [
                    Trivia("book", "Lem - Solaris"),
                    Trivia("book", "Dukaj - Starość aksolotla"),
                    Trivia("book", "Tokarczuk - Księgi Jakubowe"),
                    Trivia("book", "Lem - Eden"),
                    Trivia("book", "Mrożek - Tango"),
                    Trivia("book", "Mrożek - Policja"),
                    Trivia("book", "Piskorski - 40 i 4"),
                ],
                "tv": [
                    Trivia("movie", "Matrix"),
                    Trivia("movie", "The Lord of the rings"),
                    Trivia("movie", "Forrest Gump"),
                    Trivia("movie", "Fight club"),
                    Trivia("movie", "Inception"),
                    Trivia("series", "Breaking Bad"),
                    Trivia("series", "Rick & Morty"),
                    Trivia("series", "The Office"),
                    Trivia("series", "The Big bang Theory"),
                ],
                "podcasts": [
                    Trivia("podcast", "ancient history"),
                    Trivia("podcast", "medieval history"),
                    Trivia("podcast", "asian cooking"),
                    Trivia("podcast", "oriental cooking"),
                ],
            }
        )
