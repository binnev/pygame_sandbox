from base.animation import relative_folder, SpriteDict
from quarto import conf

folder = relative_folder(__file__, "images")


quarto_pieces = SpriteDict(
    folder=folder,
    size=conf.SPRITE_SIZE,
    scale=conf.SCALE_SPRITES,
    file_mapping={
        "tall-hollow-square-white": "tall-hollow-square-white.png",
        "tall-hollow-round-white": "tall-hollow-round-white.png",
        "tall-solid-square-white": "tall-solid-square-white.png",
        "tall-solid-round-white": "tall-solid-round-white.png",
        "short-hollow-square-white": "short-hollow-square-white.png",
        "short-hollow-round-white": "short-hollow-round-white.png",
        "short-solid-square-white": "short-solid-square-white.png",
        "short-solid-round-white": "short-solid-round-white.png",
    },
)


misc = SpriteDict(
    folder=folder,
    size=(32, 16),
    scale=3.8,
    file_mapping={
        "square": "square.png",
    },
)
