import pygame
from pygame.sprite import AbstractGroup
from robingame.input import EventQueue
from robingame.objects import PhysicalEntity

from slappers_only import images


class Character(PhysicalEntity):
    frame_duration = 5

    def __init__(self, x, y, facing_right=True):
        super().__init__()
        self.rect = pygame.Rect((x, y, 100, 200))
        self.x = x
        self.y = y
        self.facing_right = facing_right
        self.state = self.state_idle

    def state_idle(self):
        self.image = images.character_stand.loop(self.animation_frame)
        for event in EventQueue.filter(type=pygame.KEYDOWN):
            match event.key:
                case pygame.K_d:
                    self.slap()
                case pygame.K_s:
                    self.dodge()
                case pygame.K_a:
                    self.feint()

    def slap(self):

class Slap(PhysicalEntity):
    frame_duration = 5

    def __init__(self, x, y, facing_right=True):
        super().__init__()
        self.rect = pygame.Rect((x, y, 200, 100))
        self.x = x
        self.y = y
        self.facing_right = facing_right
        self.state = self.state_slap

    def state_slap(self):
        self.image = images.slap.play_once(self.animation_frame)
        if self.tick == 30:
            self.kill()
