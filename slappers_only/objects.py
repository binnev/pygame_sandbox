import pygame
from robingame.input import EventQueue
from robingame.objects import PhysicalEntity

from slappers_only import images


class Character(PhysicalEntity):
    frame_duration = 3

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

    def state_slap(self):
        self.image = images.character_slap.play(self.animation_frame)
        if not self.image:
            self.image = images.character_stand.play(0)
            self.state = self.state_idle

    def state_dodge(self):
        self.image = images.character_dodge.play_once(self.animation_frame)
        if not pygame.key.get_pressed()[pygame.K_s] or self.tick > 40:
            self.state = self.state_dodge_recovery

    def state_dodge_recovery(self):
        self.image = images.character_dodge_recovery.play(self.animation_frame)
        if not self.image:
            self.image = images.character_stand.play(0)
            self.state = self.state_idle

    def slap(self):
        """
        Todo:
        - add hitbox
        - play swing sound
        """
        print("slap")
        self.state = self.state_slap

    def dodge(self):
        print("dodge")
        self.state = self.state_dodge

    def feint(self):
        print("feint")


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
