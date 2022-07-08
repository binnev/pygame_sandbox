import pytest
from pygame import Surface, Color

from base.image import (
    SpriteAnimation,
    load_spritesheet,
    load_image_sequence,
    load_image,
    relative_folder,
    brighten_color,
)

mocks = relative_folder(__file__, "mocks")


@pytest.mark.parametrize(
    "num_images, expected_len",
    [
        (None, 3),
        (2, 2),
    ],
)
def test_load_spritesheet(num_images, expected_len, display_init):
    filename = mocks / "123_spritesheet.png"
    images = load_spritesheet(filename=filename, image_size=(64, 64), num_images=num_images)
    assert len(images) == expected_len
    assert isinstance(images[0], Surface)


def test_load_spritesheet_not_found():
    with pytest.raises(FileNotFoundError) as e:
        load_spritesheet(filename="foo/bar.png", image_size=(1, 1))
    assert str(e.value) == "Couldn't find foo/bar.png"


def test_load_image_sequence_not_found():
    with pytest.raises(FileNotFoundError) as e:
        load_image_sequence(filename="foo/bar")
    assert str(e.value) == "Couldn't find foo/bar"


@pytest.mark.parametrize(
    "num_images, expected_len",
    [
        (None, 3),
        (2, 2),
    ],
)
def test_load_image_sequence(num_images, expected_len, display_init):
    filename = mocks / "123_series.png"
    images = load_image_sequence(filename=filename, num_images=num_images)
    assert len(images) == expected_len
    assert isinstance(images[0], Surface)


def test_can_instantiate_empty_spriteanimation():
    """images=None by default and it shouldn't try to flip/recolor/scale"""
    SpriteAnimation()


def test_spriteanimation_from_spritesheet(display_init):
    filename = mocks / "123_spritesheet.png"
    anim = SpriteAnimation.from_spritesheet(filename=filename, image_size=(64, 64))
    assert isinstance(anim, SpriteAnimation)
    assert anim._images is None  # not loaded yet

    images = anim.images  # triggers .load()
    assert len(images) == 3
    assert isinstance(images[0], Surface)


def test_spriteanimation_from_image_sequence(display_init):
    filename = mocks / "123_series.png"
    anim = SpriteAnimation.from_image_sequence(filename=filename)
    assert isinstance(anim, SpriteAnimation)
    assert anim._images is None  # not loaded yet

    images = anim.images  # triggers .load()
    assert len(images) == 3
    assert isinstance(images[0], Surface)


def test_spriteanimation_from_image(display_init):
    filename = mocks / "123_spritesheet.png"
    anim = SpriteAnimation.from_image(filename=filename)
    assert isinstance(anim, SpriteAnimation)
    assert anim._images is None  # not loaded yet

    images = anim.images  # triggers .load()
    assert len(images) == 1
    assert isinstance(images[0], Surface)


def test_spriteanimation_copy_methods():
    pxl = Surface((2, 2))
    pxl.fill(Color("red"))
    pxl.set_at((0, 0), Color("black"))

    anim = SpriteAnimation(images=[pxl])
    assert anim.images[0].get_at((0, 0)) == Color("black")
    assert anim.images[0].get_at((0, 1)) == Color("red")
    assert anim.images[0].get_at((1, 0)) == Color("red")
    assert anim.images[0].get_at((1, 1)) == Color("red")

    hor_flip = anim.flipped_copy(flip_x=True)
    assert hor_flip.images[0].get_at((0, 0)) == Color("red")
    assert hor_flip.images[0].get_at((0, 1)) == Color("red")
    assert hor_flip.images[0].get_at((1, 0)) == Color("black")
    assert hor_flip.images[0].get_at((1, 1)) == Color("red")

    ver_flip = anim.flipped_copy(flip_y=True)
    assert ver_flip.images[0].get_at((0, 0)) == Color("red")
    assert ver_flip.images[0].get_at((0, 1)) == Color("black")
    assert ver_flip.images[0].get_at((1, 0)) == Color("red")
    assert ver_flip.images[0].get_at((1, 1)) == Color("red")

    recolored = anim.recolored_copy({(0, 0, 0): Color("blue")})
    assert recolored.images[0].get_at((0, 0)) == Color("blue")
    assert recolored.images[0].get_at((0, 1)) == Color("red")
    assert recolored.images[0].get_at((1, 0)) == Color("red")
    assert recolored.images[0].get_at((1, 1)) == Color("red")

    scaled = anim.scaled_copy(scale=3)
    assert anim.images[0].get_rect().width == 2
    assert anim.images[0].get_rect().height == 2
    assert scaled.images[0].get_rect().width == 6
    assert scaled.images[0].get_rect().height == 6

    # original should be unchanged
    anim = SpriteAnimation(images=[pxl])
    assert anim.images[0].get_at((0, 0)) == Color("black")
    assert anim.images[0].get_at((0, 1)) == Color("red")
    assert anim.images[0].get_at((1, 0)) == Color("red")
    assert anim.images[0].get_at((1, 1)) == Color("red")


def test_load_image_with_per_pixel_transparency(display_init):
    filename = mocks / "per_pixel_alpha.png"
    image = load_image(filename.as_posix())

    # white and red pixels should have full alpha
    for red_pixel in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        assert image.get_at(red_pixel) == (255, 0, 0, 255)
    for white_pixel in [(2, 2), (2, 3), (3, 2), (3, 3)]:
        assert image.get_at(white_pixel) == (255, 255, 255, 255)

    # green pixels should have alpha = 100
    for green_pixel in [(2, 0), (2, 1), (3, 1), (1, 3), (1, 2), (0, 2)]:
        assert image.get_at(green_pixel) == (0, 255, 0, 100)

    # corner pixels should be fully transparent
    for corner_pixel in [(3, 0), (0, 3)]:
        assert image.get_at(corner_pixel) == (0, 0, 0, 0)


def test_load_image_with_global_transparency(display_init):
    filename = mocks / "global_alpha.png"
    image = load_image(filename.as_posix())

    # white and red and green pixels should have full alpha
    for red_pixel in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        assert image.get_at(red_pixel) == (255, 0, 0, 255)
    for white_pixel in [(2, 2), (2, 3), (3, 2), (3, 3)]:
        assert image.get_at(white_pixel) == (255, 255, 255, 255)
    for green_pixel in [(2, 0), (2, 1), (3, 1), (1, 3), (1, 2), (0, 2)]:
        assert image.get_at(green_pixel) == (0, 255, 0, 255)

    # corner pixels should be fully transparent
    for corner_pixel in [(3, 0), (0, 3)]:
        assert image.get_at(corner_pixel) == (0, 0, 0, 0)


@pytest.mark.parametrize(
    "old_color, new_color",
    [
        ((0, 0, 0), (20, 20, 20)),
        (Color(0, 0, 0), (20, 20, 20)),
        ((250, 250, 250), (255, 255, 255)),
        ((255, 255, 255), (255, 255, 255)),
        ((0, 250, 255), (20, 255, 255)),
        ((0, 0, 0, 0), (20, 20, 20, 0)),  # alpha channel shouldn't change
        (Color(0, 0, 0, 0), (20, 20, 20, 0)),  # alpha channel shouldn't change
    ],
)
def test_brighten_color(old_color, new_color):
    assert brighten_color(old_color, amount=20) == new_color
