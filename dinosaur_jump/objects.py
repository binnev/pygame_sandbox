import math
import random

import pygame
from pygame import Surface, Color

from base.image import scale_image
from base.input import EventQueue
from base.objects import Entity, Group
from base.objects import PhysicalEntity
from dinosaur_jump import images, sounds


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
    gravity = 1.5

    def __init__(self, x, y) -> None:
        super().__init__()
        self.rect = pygame.rect.Rect(0, 0, 60, 60)
        self.rect.midbottom = (x, y)
        self.ground_height = y  # the height you fall back down to
        self.state = self.state_run
        self.inventory = Group()
        self.child_groups = [self.inventory]
        self.gun = None
        self.add_gun()

    def update(self):
        super().update()
        if self.gun:
            self.gun.rect.center = self.rect.midright

    def state_run(self):
        self.image = images.dino.loop(self.animation_frame)
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.jump()

    def jump(self):
        self.v = -20
        self.state = self.state_jump

    def state_jump(self):
        self.y += self.v
        self.v += self.gravity
        if self.rect.bottom >= self.ground_height:
            self.rect.bottom = self.ground_height
            self.state = self.state_run

    def add_gun(self):
        sounds.revolver_spin.play()
        self.gun = Gun(x=self.x, y=self.y)
        self.inventory.add(self.gun)


class Ptero(PhysicalEntity):
    frame_duration = 5
    speed = 10

    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.rect.Rect(0, 0, 16 * 5, 16 * 5)
        self.rect.center = (x, y)
        self.height = y
        self.state = self.state_fly

    def state_fly(self):
        self.image = images.ptero.loop(self.animation_frame)
        self.x -= self.speed
        self.y = self.height + math.sin(self.tick / 15) * 60
        # if fly off edge of screen; die
        if self.x < -10:
            self.kill()


class Cactus(PhysicalEntity):
    frame_duration = 5
    speed = 10

    def __init__(self, x, y):
        super().__init__()
        self.image = random.choice(images.cacti.images)
        self.image = self.image.subsurface(self.image.get_bounding_rect())
        self.rect = self.image.get_bounding_rect()
        self.rect.midbottom = (x, y)
        self.state = self.state_idle

    def state_idle(self):
        self.x -= self.speed
        # if fly off edge of screen; die
        if self.x < -10:
            self.kill()


class Gun(PhysicalEntity):
    def __init__(self, x, y) -> None:
        super().__init__()
        image = images.gun
        self.image = image.subsurface(image.get_bounding_rect())
        self.rect = self.image.get_bounding_rect()
        self.rect.center = (x, y)
        self.bullets = Group()
        self.child_groups = [self.bullets]

    def update(self):
        super().update()
        if EventQueue.get(type=pygame.KEYDOWN, key=pygame.K_g):
            sounds.gunshot.play()
            self.bullets.add(Bullet(x=self.rect.right, y=self.rect.centery, u=10, v=0))


class Bullet(PhysicalEntity):
    def __init__(self, x, y, u, v) -> None:
        super().__init__()
        image = images.gun
        self.image = scale_image(Surface((2, 1)), 5)
        self.image.fill(Color("gray"))
        self.rect = self.image.get_bounding_rect()
        self.rect.center = (x, y)
        self.u = u
        self.v = v
        self.state = self.state_fly

    def state_fly(self):
        self.x += self.u
        self.y += self.v
