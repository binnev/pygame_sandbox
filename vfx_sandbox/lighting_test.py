import random
import sys

import numpy
import pygame
from pygame import Color, Surface
from pygame.rect import Rect
from pygame.sprite import Sprite

from base.objects import Entity, Group


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
        self.color = color if color is not None else self.color
        self.gravity = gravity if gravity is not None else self.gravity
        self.friction = friction if friction is not None else self.friction
        self.decay = decay if decay is not None else self.decay
        self.blit_flag = blit_flag if blit_flag is not None else self.blit_flag
        self.rect = Rect(0, 0, 0, 0)
        self.x = x
        self.y = y
        self.u = u
        self.v = v
        self.radius = radius

    def update(self):
        self.x = self.x + self.u
        self.y = self.y + self.v
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
        self.particles.draw(surface)


class Fire(Fountain):
    def update(self):
        self.particles.add(
            Spark(
                self.x,
                self.y,
                u=random_float(-1, 1),
                v=-random_float(0, 1),
                radius=random_int(15, 50),
                color=(random_int(150, 175), random_int(60, 80), random_int(0, 30)),
                gravity=-0.3,
            )
        )
        self.particles.update()


class Torch(Entity):
    color = Color("orangered3")

    def __init__(self, x, y, color=None):
        super().__init__()
        self.color = color or self.color
        self.rect = Rect(0, 0, 0, 0)
        self.x = x
        self.y = y
        self.children = Group()
        block = Block(0, 0, 10, 100, Color("brown"))
        block.rect.midtop = self.x, self.y
        self.children.add(
            block,
            Glow(self.x, self.y, radius=100, variance=2, period=10, color=(20, 20, 20)),
            Glow(self.x, self.y, radius=150, variance=3, period=10, color=(20, 20, 20)),
            Fire(self.x, self.y),
        )

    def draw(self, surface: Surface, debug: bool = False):
        self.children.draw(surface, debug)

    def update(self):
        super().update()
        self.children.update()


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
                friction=0.1,
            )
        )
        self.particles.update()


class Shadow(Entity):
    blit_flag = pygame.BLEND_RGB_MULT
    gravity = 0
    decay = 0
    friction = 0
    color = (100, 100, 100)

    def __init__(self, x, y, radius, color=None, blit_flag=None, follow_object=None):
        super().__init__()
        self.color = self.color if color is None else color
        self.blit_flag = self.blit_flag if blit_flag is None else blit_flag
        self.follow_object = follow_object
        self.rect = Rect(0, 0, 0, 0)
        self.x = x
        self.y = y
        self.children = Group()
        spark_kwargs = dict(gravity=self.gravity, friction=self.friction, decay=self.decay)
        self.children.add(
            Spark(
                self.x, self.y, 0, 0, radius, color=self.color, blit_flag=blit_flag, **spark_kwargs
            ),
            Spark(
                self.x,
                self.y,
                0,
                0,
                radius + 50,
                color=self.color,
                blit_flag=blit_flag,
                **spark_kwargs
            ),
            Spark(
                self.x,
                self.y,
                0,
                0,
                radius + 100,
                color=self.color,
                blit_flag=blit_flag,
                **spark_kwargs
            ),
        )

    def update(self):
        super().update()
        self.x, self.y = pygame.mouse.get_pos()
        for child in self.children:
            child.rect.center = self.rect.center
        self.children.update()

    def draw(self, surface: Surface, debug: bool = False):
        shadow_surface = Surface((2000, 2000))
        shadow_surface.fill(Color("black"))
        self.children.draw(shadow_surface, debug)
        surface.blit(shadow_surface, shadow_surface.get_rect(), special_flags=self.blit_flag)


def circle_surf(radius, color):
    surf = Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))
    return surf


class Explosion(Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.particles = Group()
        for __ in range(50):
            self.particles.add(
                Spark(
                    x,
                    y,
                    u=random_float(-20, 20),
                    v=random_float(-50, 0),
                    radius=random_int(5, 100),
                    color=[random_int(10, 80)] * 3,
                    gravity=-0.2,
                    friction=0.2,
                    blit_flag=False,
                    decay=1.2,
                )
            )
        for __ in range(20):
            self.particles.add(
                Spark(
                    x,
                    y,
                    u=random_float(-5, 5),
                    v=-random_float(5, 10),
                    radius=random_int(30, 60),
                    color=(random_int(150, 175), random_int(60, 80), random_int(0, 30)),
                    gravity=-0.5,
                )
            )
        for __ in range(2):
            self.particles.add(
                Spark(
                    x=x + random_int(-5, 5),
                    y=y + random_int(-5, 5),
                    u=random_float(-5, 5),
                    v=random_float(-5, 5),
                    radius=random_int(100, 120),
                    color=(150, 150, 100),
                    gravity=0,
                    decay=20,
                    friction=1,
                )
            )
        for __ in range(10):
            self.particles.add(
                Spark(
                    x=x + random_int(-5, 5),
                    y=y + random_int(-5, 5),
                    u=random_float(-50, 50),
                    v=random_float(-50, 50),
                    radius=random_int(2, 7),
                    color=(200, 200, 200),
                    gravity=0.1,
                    decay=0.1,
                    friction=0.1,
                )
            )

    def update(self):
        self.particles.update()
        if not self.particles:
            self.kill()

    def draw(self, surface: Surface, debug: bool = False):
        self.particles.draw(surface, debug)


def main():
    pygame.init()
    pygame.display.init()
    clock = pygame.time.Clock()
    window = pygame.display.set_mode([1600, 900])

    # "layers"
    background = Group()
    midground = Group()
    foreground = Group()
    shadows = Group()
    groups = [
        background,
        midground,
        foreground,
        shadows,
    ]

    # add static stuff
    background.add(
        Block(300, 300, 100, 100, Color("cornsilk4")),
        Block(600, 300, 100, 100, Color("cornsilk4")),
        Torch(900, 600),
        Fountain(400, 300, color=Color("greenyellow")),
    )
    midground.add(
        Glow(400, 400, radius=100, variance=20, period=360),
        Glow(400, 400, radius=80, variance=20, period=360),
        Glow(400, 400, radius=70, variance=20, period=360),
        Glow(350, 350, radius=50, variance=10, period=100),
        Glow(400, 340, radius=40, variance=5, period=50),
        Character(100, 100),
        Torch(800, 750),
    )
    foreground.add(
        Fire(500, 300),
        Faucet(600, 300),
        Torch(800, 600),
        Block(450, 450, 333, 99, Color("dodgerblue4")),
    )
    shadows.add(Shadow(150, 150, radius=200))

    run = True
    pygame.draw.rect(window, Color("cyan"), (30, 40, 100, 200))
    max_num_entities = 0
    screen_shake = 0
    while run:

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
                    midground.add(Explosion(x, y))
                    screen_shake = 10

        for group in groups:
            group.update()

        num_entities = sum(map(len, groups))
        if num_entities > max_num_entities:
            max_num_entities = num_entities
            print(max_num_entities)

        # draw stuff
        if screen_shake:
            temp_surf = Surface(window.get_size())
            temp_surf.fill((50, 50, 50))
            screen_shake -= 1
            magnitude = 10
            dx = random.randrange(-magnitude, magnitude)
            dy = random.randrange(-magnitude, magnitude)
            rect = temp_surf.get_rect()
            rect.centerx += dx
            rect.centery += dy
            for group in groups:
                group.draw(temp_surf)
            window.blit(temp_surf, rect)
        else:
            window.fill((50, 50, 50))
            for group in groups:
                group.draw(window)
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()
