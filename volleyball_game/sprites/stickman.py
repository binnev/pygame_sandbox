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
    "fall_right": {"filename": folder / "stick_jump.png"},
    "fall_left": {"filename": folder / "stick_jump.png", "flip_horizontal": True,},
    "jump_right": {"filename": folder / "stick_jump.png"},
    "jump_left": {"filename": folder / "stick_jump.png", "flip_horizontal": True,},
    "dive_right": {"filename": folder / "stick_dive.png"},
    "dive_left": {"filename": folder / "stick_dive.png", "flip_horizontal": True,},
    "dive_getup_right": {
        "filename": folder / "stick_dive_getup.png",
        "num_images": 11,
        "looping": False,
    },
    "dive_getup_left": {
        "filename": folder / "stick_dive_getup.png",
        "flip_horizontal": True,
        "num_images": 11,
        "looping": False,
    },
    "standing_hit_right": {"filename": folder / "stick_standing_hit.png"},
    "standing_hit_left": {"filename": folder / "stick_standing_hit.png", "flip_horizontal": True},
}


def stickman_sprites():
    """I need to use a closure here because otherwise pygame kicks up a fuss about initialization"""
    return SpriteDict(
        size=(32, 32),
        scale=conf.SCALE_SPRITES,
        game_ticks_per_sprite_frame=conf.TICKS_PER_SPRITE_FRAME,
        file_mapping=file_mapping,
    )
