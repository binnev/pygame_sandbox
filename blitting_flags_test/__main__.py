import random
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


def random_float(min, max):
    assert min < max
    spread = max - min
    value = min + random.random() * spread
    return value


def random_int(min, max):
    return int(random_float(min, max))


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
    color = (50, 50, 50)

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


class Spark(Entity):
    gravity = 0.8
    friction = 0.1
    decay = 1
    color = (20, 20, 20)
    blit_flag = pygame.BLEND_RGB_ADD

    def __init__(
        self,
        x,
        y,
        u,
        v,
        radius,
        color=None,
        gravity=None,
        friction=None,
        decay=None,
        blit_flag=None,
    ):
        super().__init__()
        self.color = color or self.color
        self.gravity = gravity or self.gravity
        self.friction = friction or self.friction
        self.decay = decay or self.decay
        self.blit_flag = blit_flag if blit_flag is not None else self.blit_flag
        self.rect = Rect(0, 0, 0, 0)
        self.x = x
        self.y = y
        self.u = u
        self.v = v
        self.radius = radius

    def update(self):

        self.x = round(self.x + self.u)
        self.y = round(self.y + self.v)
        self.v += self.gravity
        self.u *= 1 - self.friction
        self.v *= 1 - self.friction
        self.radius -= self.decay
        if self.radius <= 0:
            self.kill()

    def draw(self, surface, debug=False):
        surf = circle_surf(round(self.radius), self.color)
        image_rect = surf.get_rect()
        image_rect.center = self.rect.center
        surface.blit(surf, image_rect, special_flags=self.blit_flag)


class Fountain(Entity):
    color = (20, 20, 20)

    def __init__(self, x, y, color=None):
        super().__init__()
        self.color = color or self.color
        self.rect = Rect(0, 0, 0, 0)
        self.x = x
        self.y = y
        self.particles = Group()

    def update(self):
        super().update()
        self.particles.add(
            Spark(
                self.x,
                self.y,
                u=random_float(-1, 1),
                v=-random_float(10, 15),
                radius=random_int(15, 50),
                color=self.color,
            )
        )
        self.particles.update()

    def draw(self, surface, debug=False):
        surf = circle_surf(int(20), self.color)
        image_rect = surf.get_rect()
        image_rect.center = self.rect.center
        surface.blit(surf, image_rect, special_flags=pygame.BLEND_RGB_ADD)

        self.particles.draw(surface)


class Torch(Fountain):
    def update(self):
        self.particles.add(
            Spark(
                self.x,
                self.y,
                u=random_float(-1, 1),
                v=-random_float(0, 1),
                radius=random_int(15, 50),
                color=(random_int(150, 255), random_int(100, 150), random_int(0, 50)),
                gravity=-0.3,
            )
        )
        self.particles.update()


class Faucet(Fountain):
    def update(self):
        self.particles.add(
            Spark(
                self.x,
                self.y,
                u=random_float(-2, 2),
                v=4,
                radius=15,  # random_int(15, 20),
                color=(random_int(0, 20), random_int(50, 100), random_int(150, 255)),
                gravity=0.9,
                decay=0.1,
                blit_flag=False,
                friction=0.1
            )
        )
        self.particles.update()


def circle_surf(radius, color):
    surf = Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))
    return surf


def explosion(x, y, group):
    for __ in range(50):
        group.add(
            Spark(
                x,
                y,
                u=random_float(-20, 20),
                v=random_float(-50, 0),
                radius=random_int(5, 100),
                color=[random_int(10, 80)] * 3,
                gravity=0.7,
                friction=0.2,
                blit_flag=False,
                decay=1.2
            )
        )


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
        lighting2,
        foreground,
    ]

    # add static stuff
    background.add(
        Block(300, 300, 100, 100, Color("cornsilk4")),
        Block(600, 300, 100, 100, Color("cornsilk4")),
    )
    foreground.add(Block(450, 450, 333, 99, Color("dodgerblue4")),)
    lighting.add(
        Glow(400, 400, radius=100, variance=20, period=360),
        Glow(400, 400, radius=80, variance=20, period=360),
        Glow(400, 400, radius=70, variance=20, period=360),
        Glow(350, 350, radius=50, variance=10, period=100),
        Glow(400, 340, radius=40, variance=5, period=50),
    )
    lighting2.add(
        Fountain(400, 300, color=Color("greenyellow")),
        Torch(500, 300),
        Faucet(600, 300),
    )
    # create player
    player = Character(100, 100)
    midground.add(player)

    run = True
    pygame.draw.rect(window, Color("cyan"), (30, 40, 100, 200))
    max_num_entities = 0
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
                left, middle, right = pygame.mouse.get_pressed()
                if left:
                    x, y = pygame.mouse.get_pos()
                    explosion(x, y, lighting2)

        for group in groups:
            group.update()

        num_entities = sum(map(len, groups))
        if num_entities > max_num_entities:
            max_num_entities = num_entities
            print(max_num_entities)

        # draw stuff
        for group in groups:
            group.draw(window)
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()
