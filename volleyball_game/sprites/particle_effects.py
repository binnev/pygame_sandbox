from robingame.image import SpriteDict, relative_folder
from volleyball_game import conf

folder = relative_folder(__file__, "particle_effects")

file_mapping = {
    "default": {"filename": folder / "explosion.png", "looping": False},
}


def explosion_sprites():
    return SpriteDict(
        size=(32, 32),
        scale=conf.SCALE_SPRITES,
        file_mapping=file_mapping,
    )
