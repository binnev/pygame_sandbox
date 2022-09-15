from pathlib import Path


from base.image import SpriteAnimation, load_image, scale_image

folder = Path(__file__).parent

dino = SpriteAnimation.from_spritesheet(folder / "dino.png", image_size=(16, 16), scale=5)
ptero = SpriteAnimation.from_spritesheet(folder / "pterodactyl.png", image_size=(16, 16), scale=5)
grass = scale_image(load_image(folder / "grass.png"), 5)
mountains1 = scale_image(load_image(folder / "mountains1.png"), 5)
mountains2 = scale_image(load_image(folder / "mountains2.png"), 5)
