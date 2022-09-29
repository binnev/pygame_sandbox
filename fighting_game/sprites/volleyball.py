from robingame.image import SpriteDict, relative_folder
from fighting_game import conf

folder = relative_folder(__file__, "volleyball")

volleyball_sprites = SpriteDict(
    size=conf.SPRITE_SIZE,
    scale=conf.SCALE_SPRITES,
    file_mapping=dict(default="volleyball.png"),
)
