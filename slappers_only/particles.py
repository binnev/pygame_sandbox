import random

from robingame.objects import Entity, Group, Particle
from robingame.utils import random_float, random_int


class Spittle(Entity):
    def __init__(self, x, y, right=True):
        super().__init__()
        self.particles = Group()
        self.child_groups = [
            self.particles,
        ]
        u = 20 * (1 if right else -1)
        for _ in range(10):
            self.particles.add(
                Particle(
                    x=x,
                    y=y,
                    u=u + random_float(-5, 5),
                    v=random_float(-1, 1),
                    radius=random_float(10, 15),
                    color=(230, 230, 255),
                    gravity=0.5,
                    friction=0.05,
                    blit_flag=False,
                    decay=0.5,
                )
            )

    def update(self):
        super().update()
        if not self.particles:
            self.kill()
