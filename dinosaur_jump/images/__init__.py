from pathlib import Path


from robingame.image import SpriteAnimation, load_image, scale_image

folder = Path(__file__).parent

dino = SpriteAnimation.from_spritesheet(folder / "dino.png", image_size=(16, 16), scale=5)
ptero = SpriteAnimation.from_spritesheet(folder / "pterodactyl.png", image_size=(16, 16), scale=5)
cacti = SpriteAnimation.from_spritesheet(folder / "cacti.png", image_size=(16, 16), scale=5)
keycaps = SpriteAnimation.from_spritesheet(folder / "keycap.png", image_size=(16, 16), scale=5)
cursors = SpriteAnimation.from_spritesheet(folder / "cursor.png", image_size=(16, 16), scale=5)
keycap_left = scale_image(
    load_image(folder / "keycap.png").subsurface((0, 0, 4, 16)),
    5,
)
keycap_mid = scale_image(
    load_image(folder / "keycap.png").subsurface((4, 0, 8, 16)),
    5,
)
keycap_right = scale_image(
    load_image(folder / "keycap.png").subsurface((12, 0, 4, 16)),
    5,
)
revolver_chamber = SpriteAnimation.from_spritesheet(
    folder / "revolver_chamber.png", image_size=(32, 32), scale=5
)
grass = scale_image(load_image(folder / "grass.png"), 5)
mountains1 = scale_image(load_image(folder / "mountains1.png"), 5)
mountains2 = scale_image(load_image(folder / "mountains2.png"), 5)
gun = scale_image(load_image(folder / "gun.png"), 5)
