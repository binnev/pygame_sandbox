from base.image import SpriteDict, relative_folder
from fighting_game import conf

folder = relative_folder(__file__, "hawko")


hawko_sprites = SpriteDict(
    folder=folder,
    size=conf.SPRITE_SIZE,
    scale=conf.SCALE_SPRITES,
    create_flipped_versions=True,
)
hawko_sprites.register(crouch="hawko_crouch.png")
hawko_sprites.register(run="hawko_run.png")
hawko_sprites.register(stand="hawko_stand.png")
hawko_sprites.register(fall="hawko_fall.png")
hawko_sprites.register(special_fall="hawko_special_fall.png")
hawko_sprites.register(air_dodge="hawko_air_dodge.png")
hawko_sprites.register(nair="hawko_nair.png")
hawko_sprites.register(dair="hawko_dair.png")
hawko_sprites.register(bair="hawko_bair.png")
hawko_sprites.register(fair="hawko_fair.png")
hawko_sprites.register(uair="hawko_uair.png")
hawko_sprites.register(dash_attack="hawko_nair.png")
hawko_sprites.register(jab="hawko_jab.png")
hawko_sprites.register(aerial_laser="hawko_aerial_laser.png")
hawko_sprites.register(dtilt="hawko_dtilt.png")
hawko_sprites.register(utilt="hawko_utilt.png")
hawko_sprites.register(ftilt="hawko_ftilt.png")
