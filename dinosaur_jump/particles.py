import numpy

from base.objects import Particle, Group, Entity
from base.utils import random_float, random_int


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
                Particle(
                    x,
                    y,
                    u=-2 * x_unit + random_float(-1, 1),
                    v=0 * y_unit + random_float(-1, 1),
                    radius=random_int(5, 20),
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
                    u=30 * x_unit + random_float(-5, 5),
                    v=5 * y_unit + random_float(-5, 5),
                    radius=random_int(10, 20),
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
                    u=random_float(5, 10),
                    v=0,
                    radius=random_int(20, 30),
                    color=(150, 150, 100),
                    gravity=0,
                    decay=50,
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
