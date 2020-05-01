from pathlib import Path

from platformer.conf import SCALE_SPRITES
from platformer.sprites.objects import SpriteAnimation, SpriteSheet

folder = Path("sprites/blob/")
PROJECTILE_SPRITES = {
    "right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_projectile.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES)),
    "left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_projectile.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES),
                        flip_horizontal=True),
}

folder = Path("sprites/blob/")
# todo; make a class for this. SpriteSet?
BLOB_SPRITES = {
    "stand":
        SpriteAnimation(
            SpriteSheet((folder / "blob_stand.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES)),
    "jump":
        SpriteAnimation(
            SpriteSheet((folder / "blob_jump.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "jump_right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_jump_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "jump_left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_jump_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3),
                        flip_horizontal=True),
    "fall":
        SpriteAnimation(
            SpriteSheet((folder / "blob_fall.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "fall_right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_fall_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3)),
    "fall_left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_fall_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=3),
                        flip_horizontal=True),
    "crouch":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_crouch.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES),
                        looping=False),
    "run_right":
        SpriteAnimation(
            SpriteSheet((folder / "blob_run_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=8)),
    "run_left":
        SpriteAnimation(SpriteSheet(
            (folder / "blob_run_right.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES, num_images=8),
                        flip_horizontal=True),
}

folder = Path("sprites/volleyball/")
BALL_SPRITES = {
    "default":
        SpriteAnimation(
            SpriteSheet((folder / "volleyball.png").as_posix()).load_sheet(
                32, 32, scale=SCALE_SPRITES)),
}
