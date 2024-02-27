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
                    Trivia("movie", "Matrix", forgetting_level=5e-3),
                    Trivia("movie", "The Lord of the rings", forgetting_level=5e-3),
                    Trivia("movie", "Forrest Gump", forgetting_level=5e-3),
                    Trivia("movie", "Fight club", forgetting_level=5e-3),
                    Trivia("movie", "Inception", forgetting_level=5e-3),
                    Trivia("series", "Breaking Bad", forgetting_level=5e-3),
                    Trivia("series", "Rick & Morty", forgetting_level=5e-3),
                    Trivia("series", "The Office", forgetting_level=5e-3),
                    Trivia("series", "The Big bang Theory", forgetting_level=5e-3),
                ],
                "podcasts": [
                    Trivia("podcast", "ancient history", forgetting_level=5e-3),
                    Trivia("podcast", "medieval history", forgetting_level=5e-3),
                    Trivia("podcast", "asian cooking", forgetting_level=5e-3),
                    Trivia("podcast", "oriental cooking", forgetting_level=5e-3),
                ],
            }
        )
