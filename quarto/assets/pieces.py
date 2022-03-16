from base.animation import relative_folder, SpriteDict
from quarto import conf

folder = relative_folder(__file__, "images")


quarto_pieces = SpriteDict(
    folder=folder,
    size=conf.SPRITE_SIZE,
    scale=conf.SCALE_SPRITES,
    file_mapping={
        "short-hollow-square-white": "short-hollow-square-white.png",
        "short-solid-square-white": "short-solid-square-white.png",
        "tall-hollow-square-white": "tall-hollow-square-white.png",
        "tall-solid-square-white": "tall-solid-square-white.png",
    }
)
