from base.image import SpriteAnimation, relative_folder

folder = relative_folder(__file__, "")


class flashy_button_sprites:
    idle = SpriteAnimation.from_spritesheet(
        filename=folder / "flashybutton.png",
        image_size=(32, 16),
        scale=10,
        num_images=1,
    )
    flash = SpriteAnimation.from_spritesheet(
        filename=folder / "flashybutton.png",
        image_size=(32, 16),
        scale=10,
    )
