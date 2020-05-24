from pathlib import Path

import pygame
import pytest

from platformer.objects.animation import recolor_sprite, pad_alpha
from platformer.objects.keyhandlers import KeyHandler

SCALE = 5
FPS = 60
clock = pygame.time.Clock()

pygame.init()
window = pygame.display.set_mode((500, 500))
window.fill((255, 255, 255))
key_handler = KeyHandler(queue_length=5)


def simple_game_loop(func):
    run = True
    while run:
        keys = pygame.key.get_pressed()
        key_handler.update(keys)
        pressed = key_handler.get_pressed()

        if pressed[pygame.K_ESCAPE]:
            run = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        func()
        pygame.display.flip()
        clock.tick(FPS)


@pytest.mark.parametrize(
    "bogus_colour", ((), (0,), (0, 0), (0, 0, 0, 0, 0),),
)
def test_pad_alpha(bogus_colour):
    with pytest.raises(Exception):
        pad_alpha(bogus_colour)


def test_recolor():
    filename = Path("platformer/sprites/color_test.png")
    assert filename.exists()
    assert filename.is_file()
    image = pygame.image.load(filename.as_posix()).convert_alpha()
    image = pygame.transform.scale(
        image, (image.get_rect().width * SCALE, image.get_rect().height * SCALE)
    )
    assert image

    color_mapping = {
        (255, 0, 0): (120, 62, 151),  # convert red to purple
        (0, 0, 0): (255, 163, 0),  # convert black to orange
        (0, 30, 255): (0, 163, 0),  # convert blue to green
        (195, 0, 255): (255, 255, 0),  # convert purple to yellow
    }
    result = recolor_sprite(image, color_mapping)

    def func():
        window.fill((69, 69, 69))
        window.blit(image, (0, 0))
        window.blit(result, (image.get_rect().width, 0))

    simple_game_loop(func)


def test_transparent_recolor():
    filename = Path("platformer/sprites/color_test.png")
    assert filename.exists()
    assert filename.is_file()
    image = pygame.image.load(filename.as_posix()).convert_alpha()
    image = pygame.transform.scale(
        image, (image.get_rect().width * SCALE, image.get_rect().height * SCALE)
    )
    assert image
    color_mapping = {
        (0, 0, 0, 0): (120, 62, 151, 150),  # convert transparent to translucent purple
    }

    result = recolor_sprite(image, color_mapping)

    def func():
        window.fill((69, 69, 69))
        window.blit(image, (0, 0))
        window.blit(result, (image.get_rect().width, 0))

    simple_game_loop(func)
