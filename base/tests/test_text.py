from pathlib import Path

from pygame.surface import Surface

from base.text.font import Font

TESTFONT = Path(__file__).parent.parent / "text/assets/test_font.png"
assert TESTFONT.exists()


def test_trim():
    font = Font(filename=TESTFONT, image_size=(16, 16), letters="A", trim=True)
    A = font.get("A")
    assert A.get_width() == 11  # trimmed width
    assert A.get_height() == 16  # original height


def test_render_respects_trimmed_character_size():
    font = Font(filename=TESTFONT, image_size=(16, 16), letters="A", trim=True)
    A = font.get("A")
    assert A.get_width() == 11  # trimmed width
    assert A.get_height() == 16  # original height

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
