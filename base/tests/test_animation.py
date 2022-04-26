from pathlib import Path

import pygame
import pytest

from base.image import SpriteSheet


def test_spritesheet_load_image():
    file = Path("fighting_game/sprites/volleyball/volleyball.png")
    assert file.exists() and file.is_file()
    sprite_sheet = SpriteSheet(file.as_posix(), image_size=(1, 1))
    # load() before pygame display init will result in an error
    with pytest.raises(pygame.error):
        sprite_sheet.load()
    pygame.init()
    pygame.display.set_mode((5, 5))
    sprite_sheet.load()
    pygame.quit()
