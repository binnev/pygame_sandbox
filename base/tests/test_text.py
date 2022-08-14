import string
from pathlib import Path

from pygame.surface import Surface

from base.image import load_spritesheet
from base.text.foo import Font


def test_trim(display_init):
    filename = Path(__file__).parent.parent / "text/assets/test_font.png"
    assert filename.exists()
    font = Font(
        filename=filename,
        image_size=(16, 16),
        letters=(
            string.ascii_uppercase
            + string.ascii_lowercase
            + "1234567890-=!@#$%^&*()_+[]\;',./{}|:\"<>?~`"
        ),
        trim=True,
    )
    image = font.get("a")
    assert image.get_width() == 9  # trimmed width
    assert image.get_height() == 16  # original height
    assert image.get_rect() == (0, 0, 9, 16)


def test_render(display_init):
    filename = Path(__file__).parent.parent / "text/assets/test_font.png"
    assert filename.exists()
    [A] = load_spritesheet(filename, image_size=(16, 16), num_images=1)

    font = Font(
        filename=filename,
        image_size=(16, 16),
        letters="A",
        trim=True,
    )
    A = font.get("A")
    x, y, w, h_original = A.get_rect()
    assert x == y == 0
    assert w == 11  # width affected by trim
    assert h_original == 16  # original height not affected by trim

    x, y, w, h = A.get_bounding_rect()
    assert w == 11
    assert h == 13
    assert x == 0
    assert y == 2  # from the top of the image

    surf = Surface((100, 100)).convert_alpha()
    surf.fill((0, 0, 0, 0))
    assert surf.get_bounding_rect() == (0, 0, 0, 0)

    font.render(surf, "AAA")
    assert surf.get_bounding_rect() == (0, 2, w * 3, h)
