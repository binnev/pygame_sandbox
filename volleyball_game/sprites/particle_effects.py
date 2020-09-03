from pathlib import Path

from base.animation import SpriteDict
from volleyball_game import conf

sprites_folder = Path("sprites/")
folder = sprites_folder / "particle_effects"

file_mapping = {
    "default": {"filename": folder / "explosion.png", "looping": False, "num_images": 5,},
}


def explosion_sprites():
    return SpriteDict(size=(32, 32), scale=conf.SCALE_SPRITES, file_mapping=file_mapping,)
