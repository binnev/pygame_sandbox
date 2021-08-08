from pathlib import Path

from base.animation import SpriteSheet


def test_spritesheet_load_image():
    file = Path("fighting_game/sprites/volleyball/volleyball.png")
    assert file.exists() and file.is_file()
    sprite_sheet = SpriteSheet(file.as_posix())
    sprite_sheet.load_image_file()
