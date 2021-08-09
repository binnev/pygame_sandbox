from base.animation import SpriteDict, relative_folder
from fighting_game import conf

folder = relative_folder(__file__, "stickman")

stickman_sprites = SpriteDict(
    folder=folder,
    size=conf.SPRITE_SIZE,
    scale=conf.SCALE_SPRITES,
    create_flipped_versions=True,
    file_mapping=dict(
        crouch="stick_crouch.png",
        flying_kick="stick_flying_kick.png",
        run="stick_run.png",
        stand="stick_stand.png",
        jump="stick_jump.png",
        back_air="stick_back_air.png",
        back_air2="stick_back_air2.png",
        fall="stick_jump.png",
        dive="stick_dive.png",
        dive_getup="stick_dive_getup.png",
        aerial_defense="stick_aerial_defense.png",
        standing_hit="stick_standing_hit.png",
        weird_hit="stick_weird_hit.png",
        taunt="stick_taunt.png",
        stomp="stick_stomp.png",
    ),
)
