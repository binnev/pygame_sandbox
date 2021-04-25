import random

from fighting_game.objects import *

def circle_surf(radius, color):
    radius = int(radius)
    surf = Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))
    return surf


def random_float(min, max):
    assert min < max
    spread = max - min
    value = min + random.random() * spread
    return value


def random_int(min, max):
    return int(random_float(min, max))


class Particle(PhysicalEntity):
    blit_flag = pygame.BLEND_RGB_ADD
    gravity: float
    friction: float
    decay: float
    color: Color
    radius: float

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
        if self.death_condition:
            self.kill()

    def draw(self, surface, debug=False):
        surf = circle_surf(round(self.radius), self.color)
        image_rect = surf.get_rect()
        image_rect.center = self.rect.center
        surface.blit(surf, image_rect, special_flags=self.blit_flag)

    @property
    def death_condition(self):
        return self.radius <= 0


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

        sounds.death_plume.play()
        sounds.crowd_ohh.play()

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
