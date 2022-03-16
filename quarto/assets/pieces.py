from base.animation import relative_folder, SpriteDict
from quarto import conf

folder = relative_folder(__file__, "images")


quarto_pieces = SpriteDict(
    folder=folder,
    size=conf.SPRITE_SIZE,
    scale=conf.SCALE_SPRITES,
    file_mapping={
        # "tall-hollow-square-black": "tall-hollow-square-black.png",
        # "tall-hollow-round-black": "tall-hollow-round-black.png",
        # "tall-solid-square-black": "tall-solid-square-black.png",
        # "tall-solid-round-black": "tall-solid-round-black.png",
        "tall-hollow-square-white": "tall-hollow-square-white.png",
        "tall-hollow-round-white": "tall-hollow-round-white.png",
        "tall-solid-square-white": "tall-solid-square-white.png",
        "tall-solid-round-white": "tall-solid-round-white.png",
        # "short-hollow-square-black": "short-hollow-square-black.png",
        # "short-hollow-round-black": "short-hollow-round-black.png",
        # "short-solid-square-black": "short-solid-square-black.png",
        # "short-solid-round-black": "short-solid-round-black.png",
        "short-hollow-square-white": "short-hollow-square-white.png",
        "short-hollow-round-white": "short-hollow-round-white.png",
        "short-solid-square-white": "short-solid-square-white.png",
        "short-solid-round-white": "short-solid-round-white.png",
    },
)
