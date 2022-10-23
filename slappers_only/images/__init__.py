from pathlib import Path

from robingame.image import SpriteAnimation

folder = Path(__file__).parent

character_stand = SpriteAnimation.from_spritesheet(
    folder / "character_stand.png",
    scale=5,
    image_size=(32, 32),
)
character_slap = SpriteAnimation.from_spritesheet(
    folder / "character_slap.png",
    scale=5,
    image_size=(32, 32),
)
character_dodge = SpriteAnimation.from_spritesheet(
    folder / "character_dodge.png",
    scale=5,
    image_size=(32, 32),
)
character_dodge_recovery = SpriteAnimation(
    images=[character_dodge.images[1]],
)

character_stand_flipped = SpriteAnimation(
    images=character_stand.images,
    flip_x=True,
)
character_dodge_flipped = SpriteAnimation(
    images=character_dodge.images,
    flip_x=True,
)
character_dodge_recovery_flipped = SpriteAnimation(
    images=character_dodge_recovery.images,
    flip_x=True,
)
character_slap_flipped = SpriteAnimation(
    images=character_slap.images,
    flip_x=True,
)


class character_sprites:
    stand = character_stand
    dodge = character_dodge
    dodge_recovery = character_dodge_recovery
    slap = character_slap


class character_sprites_flipped:
    stand = character_stand_flipped
    dodge = character_dodge_flipped
    dodge_recovery = character_dodge_recovery_flipped
    slap = character_slap_flipped
