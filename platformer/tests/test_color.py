import os
from pathlib import Path

import pygame

from platformer.conf import SCALE_SPRITES
from platformer.sprites import SpriteAnimation, SpriteSheet
from platformer.utils import recolor

pygame.init()
window = pygame.display.set_mode((500, 500))
window.fill((255, 255, 255))


def test_recolor():
    filename = Path("platformer/sprites/blob/blob_run_right.png")
    cwd = os.getcwd()
    assert filename.exists()
    assert filename.is_file()
    image = pygame.image.load(filename.as_posix()).convert_alpha()
    assert image
    color_mapping = {
        (120, 62, 151): (255, 0, 0),  # convert purple to red
        (0, 0, 0): (255, 163, 0),  # convert black to orange
    }
    result = recolor(image, color_mapping)
    spritesheet = SpriteSheet(filename.as_posix())
    animation = SpriteAnimation(
        spritesheet.load_sheet(32, 32, scale=SCALE_SPRITES, num_images=8))
    window.blit(result, (0, 0))
    print("")
