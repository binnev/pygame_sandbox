import math

import numpy
import pygame

from base.objects import Particle, Group, Entity
from base.utils import random_float, random_int


class Particle(Particle):
    def __init__(
        self,
        x,
        y,
        velocity=0,
        angle_deg=0,
        radius=None,
        color=None,
        gravity=None,
        friction=None,
        decay=None,
        blit_flag=None,
    ):
        angle_rad = math.radians(angle_deg)
        u = velocity * math.cos(angle_rad)
        v = -velocity * math.sin(angle_rad)
        super().__init__(x, y, u, v, radius, color, gravity, friction, decay, blit_flag)

    def draw(self, surface, debug=False):
        surf = pygame.Surface((self.radius, self.radius)).convert_alpha()
        surf.fill(self.color)
        image_rect = surf.get_rect()
        image_rect.center = self.rect.center
        surface.blit(surf, image_rect, special_flags=self.blit_flag)


class GunShot(Entity):
    def __init__(self, x, y, angle_deg):
        super().__init__()
        self.state = self.state_main
        self.x = x
        self.y = y
        self.particles = Group()
        self.child_groups = [self.particles]
        x_unit = numpy.cos(numpy.deg2rad(angle_deg))
        y_unit = -numpy.sin(numpy.deg2rad(angle_deg))

        # smoke
        for _ in range(10):
            self.particles.add(
                Particle(
                    x + 20 * x_unit,
                    y,
                    velocity=5 * x_unit + random_float(-1, 1),
                    angle_deg=angle_deg,
                    radius=random_int(5, 20) * 2,
                    color=[random_int(10, 80)] * 3,
                    gravity=-0.3,
                    friction=0.05,
                    blit_flag=False,
                    decay=0.3,
                )
            )
        # flames
        for _ in range(10):
            self.particles.add(
                Particle(
                    x,
                    y,
                    velocity=30 * x_unit + random_float(-5, 5),
                    angle_deg=angle_deg,
                    radius=random_int(10, 20) * 2,
                    color=(random_int(150, 175), random_int(60, 80), random_int(0, 30)),
                    gravity=-0.5,
                    decay=1,
                    friction=0.1,
                )
            )
        # white flashes
        for _ in range(2):
            self.particles.add(
                Particle(
                    x=x + 15,
                    y=y,
                    velocity=random_float(5, 10),
                    angle_deg=angle_deg,
                    radius=100,
                    color=(150, 150, 100),
                    gravity=0,
                    decay=40,
                    friction=1,
                )
            )
        # sparks
        for _ in range(20):
            self.particles.add(
                Particle(
                    x=x,
                    y=y,
                    velocity=20 + random_float(-10, 10),
                    angle_deg=angle_deg + random_float(-1, 1),
                    radius=random_int(2, 7) * 2,
                    color=(200, 200, 200),
                    gravity=0.1,
                    decay=0.2,
                    friction=0.1,
                )
            )

    def state_main(self):
        if not self.particles:
            self.kill()
