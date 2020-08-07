from pathlib import Path

from base.animation import SpriteDict
from volleyball_game import conf

sprites_folder = Path("sprites/")
folder = sprites_folder / "stickman"

# todo: make something to automatically create left-facing versions?
file_mapping = {
    "crouch_right": {"filename": folder / "stick_crouch.png"},
    "crouch_left": {"filename": folder / "stick_crouch.png", "flip_horizontal": True,},
    "stand_right": {"filename": folder / "stick_stand.png"},
    "stand_left": {"filename": folder / "stick_stand.png", "flip_horizontal": True,},
    "run_right": {"filename": folder / "stick_run.png"},
    "run_left": {"filename": folder / "stick_run.png", "flip_horizontal": True,},
    # dummy stuff:
    "fall": {"filename": folder / "stick_jump.png"},
    "fall_right": {"filename": folder / "stick_jump.png"},
    "fall_left": {"filename": folder / "stick_jump.png", "flip_horizontal": True,},
    "jump": {"filename": folder / "stick_jump.png"},
    "jump_right": {"filename": folder / "stick_jump.png"},
    "jump_left": {"filename": folder / "stick_jump.png", "flip_horizontal": True,},
}


def stickman_sprites():
    """I need to use a closure here because otherwise pygame kicks up a fuss about initialization"""
    return SpriteDict(
        size=(32, 32),
        scale=conf.SCALE_SPRITES,
        game_ticks_per_sprite_frame=conf.TICKS_PER_SPRITE_FRAME,
        file_mapping=file_mapping,
    )
