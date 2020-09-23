from base.animation import SpriteDict, relative_folder
from volleyball_game import conf

folder = relative_folder(__file__, "stickman")

# todo: make something to automatically create left-facing versions?
# todo: make this a dict of SpriteAnimations so that they can autocomplete arguments. Use a
#  defaults dict to supply shared params.
#  don't forget to wrap the whole thing in a function so that it doesn't complain about display
#  initialisation
file_mapping = {
    "crouch_right": {"filename": folder / "stick_crouch.png"},
    "crouch_left": {"filename": folder / "stick_crouch.png", "flip_horizontal": True,},
    "stand_right": {"filename": folder / "stick_stand.png"},
    "stand_left": {"filename": folder / "stick_stand.png", "flip_horizontal": True,},
    "run_right": {"filename": folder / "stick_run.png", "num_images": 8,},
    "run_left": {"filename": folder / "stick_run.png", "num_images": 8, "flip_horizontal": True,},
    "flying_kick_right": {
        "filename": folder / "stick_flying_kick.png",
        "num_images": 7,
        "looping": False,
    },
    "flying_kick_left": {
        "filename": folder / "stick_flying_kick.png",
        "num_images": 7,
        "flip_horizontal": True,
        "looping": False,
    },
    "back_air_right": {
        "filename": folder / "stick_back_air.png",
        "num_images": 7,
        "looping": False,
    },
    "back_air_left": {
        "filename": folder / "stick_back_air.png",
        "num_images": 7,
        "flip_horizontal": True,
        "looping": False,
    },
    "back_air2_right": {
        "filename": folder / "stick_back_air2.png",
        "num_images": 5,
        "looping": False,
    },
    "back_air2_left": {
        "filename": folder / "stick_back_air2.png",
        "num_images": 5,
        "flip_horizontal": True,
        "looping": False,
    },
    "fall_right": {"filename": folder / "stick_jump.png"},
    "fall_left": {"filename": folder / "stick_jump.png", "flip_horizontal": True,},
    "jump_right": {"filename": folder / "stick_jump.png", "num_images": 3},
    "jump_left": {"filename": folder / "stick_jump.png", "num_images": 3, "flip_horizontal": True,},
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
    "aerial_defense_right": {"filename": folder / "stick_aerial_defense.png", "num_images": 3},
    "aerial_defense_left": {
        "filename": folder / "stick_aerial_defense.png",
        "flip_horizontal": True,
        "num_images": 3,
    },
    "standing_hit_right": {"filename": folder / "stick_standing_hit.png"},
    "standing_hit_left": {"filename": folder / "stick_standing_hit.png", "flip_horizontal": True},
    "weird_hit_right": {
        "filename": folder / "stick_weird_hit.png",
        "looping": False,
        "num_images": 5,
    },
    "weird_hit_left": {
        "filename": folder / "stick_weird_hit.png",
        "looping": False,
        "num_images": 5,
        "flip_horizontal": True,
    },
    "taunt_right": {"filename": folder / "stick_taunt.png", "looping": False, "num_images": 14,},
    "taunt_left": {
        "filename": folder / "stick_taunt.png",
        "looping": False,
        "num_images": 14,
        "flip_horizontal": True,
    },
    "stomp_right": {"filename": folder / "stick_stomp.png", "looping": False, "num_images": 6,},
    "stomp_left": {
        "filename": folder / "stick_stomp.png",
        "looping": False,
        "num_images": 6,
        "flip_horizontal": True,
    },
}


def stickman_sprites():
    """I need to use a closure here because otherwise pygame kicks up a fuss about initialization"""
    return SpriteDict(size=(32, 32), scale=conf.SCALE_SPRITES, file_mapping=file_mapping,)
