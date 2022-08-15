import string
from pathlib import Path

import pygame

from base.text.font import Font

pygame.display.init()
window = pygame.display.set_mode((1, 1))

assets = Path(__file__).parent.parent / "assets"

test_font = Font(
    filename=assets / "test_font.png",
    image_size=(16, 16),
    letters=(
        string.ascii_uppercase
        + string.ascii_lowercase
        + "1234567890-=!@#$%^&*()_+[]\;',./{}|:\"<>?~`"
    ),
    trim=True,
    xpad=1,
    space_width=8,
)

cellphone_black = Font(
    filename=assets / "cellphone-black.png",
    image_size=(7, 9),
    letters=(
        """!"#$%&'()*+,-./0123456789:'<=>?@"""
        + string.ascii_uppercase
        + "[\]^_`"
        + string.ascii_lowercase
        + "{|}~"
    ),
    xpad=1,
    colorkey=-1,
    trim=True,
    space_width=4,
)
cellphone_white = Font(
    filename=assets / "cellphone-white.png",
    image_size=(7, 9),
    letters=(
        """!"#$%&'()*+,-./0123456789:'<=>?@"""
        + string.ascii_uppercase
        + "[\]^_`"
        + string.ascii_lowercase
        + "{|}~"
    ),
    xpad=1,
    colorkey=-1,
    trim=True,
    space_width=4,
)
