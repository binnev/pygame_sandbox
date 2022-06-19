from pathlib import Path

import pytest
from pygame import Surface

from base.image import SpriteAnimation, load_spritesheet, load_image_sequence, SpriteSheet


@pytest.mark.parametrize(
    "num_images, expected_len",
    [
        (None, 3),
        (2, 2),
    ],
)
def test_load_spritesheet(num_images, expected_len, display_init):
    filename = Path(__file__).parent / "test_assets" / "123_spritesheet.png"
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
    filename = Path(__file__).parent / "test_assets" / "123_series.png"
    images = load_image_sequence(filename=filename, num_images=num_images)
    assert len(images) == expected_len
    assert isinstance(images[0], Surface)


def test_can_instantiate_empty_spriteanimation():
    """images=None by default and it shouldn't try to flip/recolor/scale"""
    SpriteAnimation()


def test_spriteanimation_from_spritesheet(display_init):
    filename = Path(__file__).parent / "test_assets" / "123_spritesheet.png"
    anim = SpriteAnimation.from_spritesheet(filename=filename, image_size=(64, 64))
    assert isinstance(anim, SpriteAnimation)
    assert anim._images is None  # not loaded yet

    images = anim.images  # triggers .load()
    assert len(images) == 3
    assert isinstance(images[0], Surface)


def test_spriteanimation_from_image_sequence(display_init):
    filename = Path(__file__).parent / "test_assets" / "123_series.png"
    anim = SpriteAnimation.from_image_sequence(filename=filename)
    assert isinstance(anim, SpriteAnimation)
    assert anim._images is None  # not loaded yet

    images = anim.images  # triggers .load()
    assert len(images) == 3
    assert isinstance(images[0], Surface)
