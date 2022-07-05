import pygame
from pygame import Rect
from pygame.color import Color

from base.objects.entity import PhysicalEntity
from base.utils import circle_surf


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
