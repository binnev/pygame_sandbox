from base.animation import SpriteDict, relative_folder, SpriteSheet, SpriteAnimation
from volleyball_game import conf

folder = relative_folder(__file__, "hawko")

SPRITE_SIZE = (32, 32)


def hawko_sprites():
    crouch = SpriteSheet(filename=folder / "hawko_crouch.png")
    run = SpriteSheet(filename=folder / "hawko_run.png")
    stand = SpriteSheet(filename=folder / "hawko_stand.png")
    fall = SpriteSheet(filename=folder / "hawko_fall.png")
    special_fall = SpriteSheet(filename=folder / "hawko_special_fall.png")
    air_dodge = SpriteSheet(filename=folder / "hawko_air_dodge.png")

    nair = SpriteSheet(filename=folder / "hawko_nair.png")
    dair = SpriteSheet(filename=folder / "hawko_dair.png")
    bair = SpriteSheet(filename=folder / "hawko_bair.png")
    # fair = SpriteSheet(filename=folder / "hawko_fair.png")
    uair = SpriteSheet(filename=folder / "hawko_uair.png")

    dash_attack = SpriteSheet(filename=folder / "hawko_nair.png")
    jab = SpriteSheet(filename=folder / "hawko_jab.png")
    dtilt = SpriteSheet(filename=folder / "hawko_dtilt.png")

    aerial_laser = SpriteSheet(filename=folder / "hawko_aerial_laser.png")

    # describe the animations -- do they loop, etc -- once here
    animations = dict(
        stand=SpriteAnimation(stand.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        run=SpriteAnimation(run.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        crouch=SpriteAnimation(crouch.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        fall=SpriteAnimation(fall.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        special_fall=SpriteAnimation(
            special_fall.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES
        ),
        air_dodge=SpriteAnimation(air_dodge.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        nair=SpriteAnimation(nair.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        dair=SpriteAnimation(dair.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        bair=SpriteAnimation(bair.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        # fair=SpriteAnimation(fair.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        uair=SpriteAnimation(uair.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        jab=SpriteAnimation(jab.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        dtilt=SpriteAnimation(dtilt.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        dash_attack=SpriteAnimation(
            dash_attack.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES
        ),
        aerial_laser=SpriteAnimation(
            aerial_laser.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES
        ),
    )

    # automatically create flipped versions
    two_sided_animations = {}
    for name, animation in animations.items():
        two_sided_animations[name + "_right"] = animation
        two_sided_animations[name + "_left"] = animation.copy(flip_x=True)

    sprite_dict = SpriteDict(file_mapping={})
    sprite_dict.update(two_sided_animations)

    return sprite_dict
