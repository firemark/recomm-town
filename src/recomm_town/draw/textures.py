from pyglet.image import ImageGrid, load as image_load
from recomm_town.draw.consts import TEXTURES
from recomm_town.human.activity import Activity

ACTIVITY_SPRITES = ImageGrid(image_load(TEXTURES / "activities.png"), len(Activity), 3)
ROOM_SPRITES = ImageGrid(image_load(TEXTURES / "rooms.png"), 8, 3)
LEVEL_SPRITES = ImageGrid(image_load(TEXTURES / "levels.png"), 4, 1)
HUMAN_SPRITE = image_load(TEXTURES / "human.png")
LEARNBAR_IMAGE = image_load(TEXTURES / "learnbar.png")