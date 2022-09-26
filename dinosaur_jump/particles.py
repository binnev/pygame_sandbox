import math

import numpy

from base.objects import SquareParticle, Group, Entity
from base.utils import random_float, random_int


class Particle(SquareParticle):
    def __init__(
        self,
        x,
        y,
        velocity=0,
        angle=0,
        radius=None,
        color=None,
        gravity=None,
        friction=None,
        decay=None,
        blit_flag=None,
    ):
        angle = math.degrees(angle)
        u = velocity * math.cos(angle)
        v = velocity * math.sin(angle)
        super().__init__(x, y, u, v, radius, color, gravity, friction, decay, blit_flag)


class GunShot(Entity):
    def __init__(self, x, y, angle_deg):
        super().__init__()
        self.state = self.state_main
        self.x = x
        self.y = y
        self.particles = Group()
        self.child_groups = [self.particles]
        # grey clouds
        x_unit = numpy.cos(numpy.deg2rad(angle_deg))
        y_unit = -numpy.sin(numpy.deg2rad(angle_deg))

        # smoke
        for _ in range(10):
            self.particles.add(
                SquareParticle(
                    x + 20 * x_unit,
                    y,
                    u=5 * x_unit + random_float(-1, 1),
                    v=0 * y_unit + random_float(-1, 1),
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
                SquareParticle(
                    x,
                    y,
                    u=30 * x_unit + random_float(-5, 5),
                    v=5 * y_unit + random_float(-5, 5),
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
                SquareParticle(
                    x=x + 15,
                    y=y,
                    u=random_float(5, 10),
                    v=0,
                    radius=random_int(20, 30) * 2,
                    color=(150, 150, 100),
                    gravity=0,
                    decay=50,
                    friction=1,
                )
            )
        # sparks
        for _ in range(20):
            self.particles.add(
                SquareParticle(
                    x=x + random_int(-1, 1) * x_unit,
                    y=y + random_int(-1, 1) * y_unit,
                    u=40 * x_unit + random_float(-2, 2),
                    v=40 * y_unit + random_float(-2, 2),
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
