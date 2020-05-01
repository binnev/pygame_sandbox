from pathlib import Path

import pygame

from platformer.objects.animation import recolor_sprite

SCALE = 5
FPS = 60
clock = pygame.time.Clock()

pygame.init()
window = pygame.display.set_mode((500, 500))
window.fill((255, 255, 255))


def simple_game_loop(func):
    run = True
    while run:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            run = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        func()
        pygame.display.flip()
        clock.tick(FPS)


def test_recolor():
    filename = Path("platformer/sprites/color_test.png")
    assert filename.exists()
    assert filename.is_file()
    image = pygame.image.load(filename.as_posix()).convert_alpha()
    image = pygame.transform.scale(image,
                                   (image.get_rect().width * SCALE,
                                    image.get_rect().height * SCALE))
    assert image

    color_mapping = {
        (255, 0, 0): (120, 62, 151),  # convert red to purple
        (0, 0, 0): (255, 163, 0),  # convert black to orange
        (0, 30, 255): (0, 163, 0),  # convert blue to green
        (195, 0, 255): (255, 255, 0),  # convert purple to yellow
    }
    result = recolor_sprite(image, color_mapping)

    def func():
        window.fill((0, 100, 0))
        window.blit(image, (0, 0))
        window.blit(result, (image.get_rect().width, 0))

    simple_game_loop(func)
    print("")
