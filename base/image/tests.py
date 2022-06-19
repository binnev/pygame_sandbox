from pathlib import Path

import pygame
import pytest

from base.image import SpriteAnimation, load_spritesheet, load_image_sequence


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
    assert isinstance(images[0], pygame.Surface)


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
    assert isinstance(images[0], pygame.Surface)


def test_can_instantiate_empty_spriteanimation():
    """images=None by default and it shouldn't try to flip/recolor/scale"""
    SpriteAnimation()
