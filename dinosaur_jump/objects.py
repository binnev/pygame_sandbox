import math
import random
import pygame
from pygame import Surface

from base.objects import Entity
from base.objects import PhysicalEntity
from dinosaur_jump import images


class ScrollingBackground(Entity):
    def __init__(self, x, y, image: Surface, speed: int):
        super().__init__()
        self.x = x
        self.y = y
        self.image = image
        self.speed = speed
        self.progress = 0

    def draw(self, surface: Surface, debug: bool = False):
        surface.blit(self.image, (self.x - self.progress, self.y))
        surface.blit(self.image, (self.x - self.progress + self.image.get_width(), self.y))

    def update(self):
        self.progress = (self.progress + self.speed) % self.image.get_width()


class Dino(PhysicalEntity):
    frame_duration = 5

    def __init__(self, x, y) -> None:
        super().__init__()
        self.rect = pygame.rect.Rect(0, 0, 60, 60)
        self.rect.center = (x, y)
        self.state = self.state_run

    def state_run(self):
        self.image = images.dino.loop(self.animation_frame)
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.x += 5
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.x -= 5
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.y += 5
        if pygame.key.get_pressed()[pygame.K_UP]:
            self.y -= 5


class Ptero(PhysicalEntity):
    frame_duration = 5

    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.rect.Rect(0, 0, 16 * 5, 16 * 5)
        self.rect.center = (x, y)
        self.height = y
        self.state = self.state_fly

    def state_fly(self):
        self.image = images.ptero.loop(self.animation_frame)
        self.x -= 10
        self.y = self.height + math.sin(self.tick / 15) * 60
        # if fly off edge of screen; die
        if self.x < -10:
            self.kill()


class Cactus(PhysicalEntity):
    frame_duration = 5

    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.rect.Rect(0, 0, 16 * 5, 16 * 5)
        self.rect.center = (x, y)
        self.state = self.state_idle
        self.image = random.choice(images.cacti.images)

    def state_idle(self):
        self.x -= 10
        # if fly off edge of screen; die
        if self.x < -10:
            self.kill()
