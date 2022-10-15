from pathlib import Path

from robingame.image import SpriteAnimation

folder = Path(__file__).parent

character_stand = SpriteAnimation.from_spritesheet(
    folder / "character_stand.png",
    scale=5,
    image_size=(32, 64),
)
character_stand_flipped = SpriteAnimation.from_spritesheet(
    folder / "character_stand.png",
    scale=5,
    image_size=(32, 64),
    flip_x=True,
)


slap = SpriteAnimation.from_spritesheet(
    folder / "slap.png",
    image_size=(64, 32),
    scale=5,
)
slap_flipped = SpriteAnimation.from_spritesheet(
    folder / "slap.png",
    image_size=(64, 32),
    scale=5,
    flip_x=True,
)
