from base.image import SpriteDict, relative_folder
from fighting_game import conf

folder = relative_folder(__file__, "hawko")


hawko_sprites = SpriteDict(
    folder=folder,
    size=conf.SPRITE_SIZE,
    scale=conf.SCALE_SPRITES,
    create_flipped_versions=True,
    file_mapping=dict(
        crouch="hawko_crouch.png",
        run="hawko_run.png",
        stand="hawko_stand.png",
        fall="hawko_fall.png",
        special_fall="hawko_special_fall.png",
        air_dodge="hawko_air_dodge.png",
        nair="hawko_nair.png",
        dair="hawko_dair.png",
        bair="hawko_bair.png",
        fair="hawko_fair.png",
        uair="hawko_uair.png",
        dash_attack="hawko_nair.png",
        jab="hawko_jab.png",
        dtilt="hawko_dtilt.png",
        utilt="hawko_utilt.png",
        ftilt="hawko_ftilt.png",
        aerial_laser="hawko_aerial_laser.png",
    ),
)
