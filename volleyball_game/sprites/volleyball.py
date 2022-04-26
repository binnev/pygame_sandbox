from base.image import SpriteDict, relative_folder
from volleyball_game import conf

folder = relative_folder(__file__, "volleyball")

file_mapping = {
    "default": {"filename": folder / "volleyball.png"},
}


def volleyball_sprites():
    return SpriteDict(
        size=(32, 32),
        scale=conf.SCALE_SPRITES,
        file_mapping=file_mapping,
    )
