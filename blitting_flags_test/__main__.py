import sys

import pygame
from pygame import Color, Surface, BLEND_RGB_ADD

from fighting_game.groups import Group


def circle_surf(radius, color):
    surf = Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))
    return surf


def main():
    pygame.init()
    pygame.display.init()
    window = pygame.display.set_mode([1600, 900])
    foreground = Surface(window.get_size())
    background = Surface(window.get_size())
    foreground.set_colorkey((0, 0, 0, 0))
    background.set_colorkey((0, 0, 0, 0))

    run = True
    pygame.draw.rect(window, Color("cyan"), (30, 40, 100, 200))
    while run:
        window.fill((0, 0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                left, middle, right = pygame.mouse.get_pressed()
                # currently drawing with full alpha onto fg/bg surfaces. Need to also use
                # blitting here if I want to have transparency between objects on the same layer.
                if left:
                    circle = circle_surf(50, (100, 50, 69, 100))
                    foreground.blit(
                        circle, (x, y), special_flags=pygame.BLEND_RGB_ADD,
                    )
                if right:
                    pygame.draw.rect(background, (0, 30, 50), (x, y, 100, 100))

        # draw stuff
        window.blit(background, background.get_rect())  # todo: flags
        window.blit(foreground, foreground.get_rect(), special_flags=pygame.BLEND_RGB_ADD)
        pygame.display.update()


if __name__ == "__main__":
    main()
