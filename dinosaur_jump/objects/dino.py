import pygame
from pygame.sprite import AbstractGroup

from base.objects import PhysicalEntity
from dinosaur_jump import images


class Dino(PhysicalEntity):
    frame_duration = 5

    def __init__(self, x, y) -> None:
        super().__init__()
        self.rect = pygame.rect.Rect(0, 0, 50, 50)
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

    def update(self):
        super().update()



