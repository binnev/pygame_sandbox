import sys

import numpy
import pygame
from pygame import Color, Surface
from pygame.rect import Rect

from fighting_game.groups import Group
from fighting_game.objects import Entity


def sin_values(mean, variance, n_points):
    xs = numpy.linspace(0, numpy.pi * 2, n_points)
    ys = numpy.sin(xs)
    ys = ys * variance + mean
    return ys


class Character(Entity):
    width = 40
    height = 60
    color = Color("orange")
    speed = 3

    def __init__(self, x, y):
        super().__init__()
        self.rect = Rect(0, 0, self.width, self.height)
        self.x = x
        self.y = y
        self.image = Surface((self.width, self.height))
        self.image.fill(self.color)
        pygame.draw.rect(self.image, Color("brown"), self.image.get_rect(), 10)

    def update(self):
        super().update()
        if pygame.key.get_pressed()[pygame.K_w]:
            self.y -= self.speed
        if pygame.key.get_pressed()[pygame.K_s]:
            self.y += self.speed
        if pygame.key.get_pressed()[pygame.K_a]:
            self.x -= self.speed
        if pygame.key.get_pressed()[pygame.K_d]:
            self.x += self.speed


class Block(Entity):
    color = Color("gray")

    def __init__(self, x, y, width, height, color=None):
        super().__init__()
        self.color = color or self.color
        self.rect = Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.image = Surface((width, height))
        self.image.fill(self.color)


class Glow(Entity):
    color = (30, 30, 30)

    def __init__(self, x, y, radius, color=None, variance=0, period=0):
        super().__init__()
        self.color = color or self.color
        self.variance = variance
        self.period = period
        self.radius = radius
        self.rect = Rect(0, 0, 0, 0)
        self.rect.center = (x, y)

    def draw(self, surface, debug=False):
        radii = sin_values(self.radius, self.variance, self.period)
        radius = int(radii[self.game_tick % len(radii)])
        surf = circle_surf(radius, self.color)
        image_rect = surf.get_rect()
        image_rect.center = self.rect.center
        surface.blit(surf, image_rect, special_flags=pygame.BLEND_RGB_ADD)


def circle_surf(radius, color):
    surf = Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))
    return surf


def main():
    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()
    window = pygame.display.set_mode([1600, 900])

    # "layers"
    background = Group()
    midground = Group()
    foreground = Group()
    lighting = Group()
    lighting2 = Group()
    groups = [
        background,
        midground,
        lighting,
        foreground,
        lighting2,
    ]

    # add static stuff
    background.add(
        Block(100, 100, 100, 100, Color("cornsilk4")),
        Block(400, 100, 100, 100, Color("cornsilk4")),
    )
    foreground.add(Block(250, 250, 333, 99, Color("dodgerblue4")),)
    lighting.add(
        Glow(200, 200, radius=100, variance=20, period=360),
        Glow(200, 200, radius=80, variance=20, period=360),
        Glow(200, 200, radius=70, variance=20, period=360),
        Glow(150, 150, radius=50, variance=10, period=100),
        Glow(200, 140, radius=40, variance=5, period=50),
    )
    # create player
    player = Character(0, 0)
    midground.add(player)

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

        for group in groups:
            group.update()

        # draw stuff
        for group in groups:
            group.draw(window)
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()
