from base.animation import SpriteDict, relative_folder, SpriteSheet, SpriteAnimation
from volleyball_game import conf

folder = relative_folder(__file__, "stickman")

# todo: make something to automatically create left-facing versions?
# todo: make this a dict of SpriteAnimations so that they can autocomplete arguments. Use a
#  defaults dict to supply shared params.
#  don't forget to wrap the whole thing in a function so that it doesn't complain about display
#  initialisation

SPRITE_SIZE = (32, 32)


def stickman_sprites():
    """I need to use a closure here because otherwise pygame kicks up a fuss about initialization"""

    # instantiate the spritesheets here
    crouch = SpriteSheet(filename=folder / "stick_crouch.png")
    flying_kick = SpriteSheet(filename=folder / "stick_flying_kick.png")
    run = SpriteSheet(filename=folder / "stick_run.png")
    stand = SpriteSheet(filename=folder / "stick_stand.png")
    jump = SpriteSheet(filename=folder / "stick_jump.png")
    back_air = SpriteSheet(filename=folder / "stick_back_air.png")
    back_air2 = SpriteSheet(filename=folder / "stick_back_air2.png")
    fall = SpriteSheet(filename=folder / "stick_jump.png")
    dive = SpriteSheet(filename=folder / "stick_dive.png")
    dive_getup = SpriteSheet(filename=folder / "stick_dive_getup.png")
    aerial_defense = SpriteSheet(filename=folder / "stick_aerial_defense.png")
    standing_hit = SpriteSheet(filename=folder / "stick_standing_hit.png")
    weird_hit = SpriteSheet(filename=folder / "stick_weird_hit.png")
    taunt = SpriteSheet(filename=folder / "stick_taunt.png")
    stomp = SpriteSheet(filename=folder / "stick_stomp.png")

    # describe the animations -- do they loop, etc -- once here
    animations = dict(
        stand=SpriteAnimation(stand.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        run=SpriteAnimation(run.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        crouch=SpriteAnimation(crouch.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        jump=SpriteAnimation(jump.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        back_air=SpriteAnimation(
            back_air.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES, looping=False
        ),
        back_air2=SpriteAnimation(
            back_air2.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES, looping=False
        ),
        fall=SpriteAnimation(fall.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        dive=SpriteAnimation(dive.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES),
        dive_getup=SpriteAnimation(
            dive_getup.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES, looping=False
        ),
        aerial_defense=SpriteAnimation(
            aerial_defense.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES
        ),
        standing_hit=SpriteAnimation(
            standing_hit.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES
        ),
        weird_hit=SpriteAnimation(
            weird_hit.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES, looping=False
        ),
        taunt=SpriteAnimation(
            taunt.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES, looping=False
        ),
        stomp=SpriteAnimation(
            stomp.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES, looping=False
        ),
        flying_kick=SpriteAnimation(
            flying_kick.get_images(size=SPRITE_SIZE), scale=conf.SCALE_SPRITES, looping=False
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
