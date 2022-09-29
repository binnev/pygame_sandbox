import numpy

from robingame.objects import Entity, Group, Particle
from robingame.utils import random_float, random_int


class Plume(Entity):
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

        for _ in range(25):
            self.particles.add(
                Particle(
                    x,
                    y,
                    u=30 * x_unit + random_float(-10, 10),
                    v=30 * y_unit + random_float(-10, 10),
                    radius=random_int(5, 100),
                    color=[random_int(10, 80)] * 3,
                    gravity=-0.2,
                    friction=0.05,
                    blit_flag=False,
                    decay=1.2,
                )
            )
        # flames
        for _ in range(15):
            self.particles.add(
                Particle(
                    x,
                    y,
                    u=30 * x_unit + random_float(-5, 5),
                    v=30 * y_unit + random_float(-5, 5),
                    radius=random_int(30, 60),
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
        # sparks
        for _ in range(20):
            self.particles.add(
                Particle(
                    x=x + random_int(-5, 5),
                    y=y + random_int(-5, 5),
                    u=40 * x_unit + random_float(-15, 15),
                    v=40 * y_unit + random_float(-15, 15),
                    radius=random_int(2, 7),
                    color=(200, 200, 200),
                    gravity=0.1,
                    decay=0.2,
                    friction=0.1,
                )
            )

    def state_main(self):
        if not self.particles:
            self.kill()
