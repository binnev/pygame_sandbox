import pygame
from robingame.input import EventQueue
from robingame.objects import PhysicalEntity

from slappers_only import images
from slappers_only.images import character_sprites, character_sprites_flipped
from slappers_only.inputs import KeyboardPlayer1, KeyboardPlayer2


class Character(PhysicalEntity):
    frame_duration = 3

    def __init__(self, x, y, facing_right=True):
        super().__init__()
        self.rect = pygame.Rect((x, y, 100, 200))
        self.x = x
        self.y = y
        self.facing_right = facing_right
        self.state = self.state_idle
        self.sprites = character_sprites if facing_right else character_sprites_flipped
        self.k_slap = pygame.K_d if facing_right else pygame.K_j
        self.k_dodge = pygame.K_s if facing_right else pygame.K_k
        self.k_feint = pygame.K_a if facing_right else pygame.K_l

    def state_idle(self):
        self.image = self.sprites.stand.loop(self.animation_frame)
        for event in EventQueue.filter(type=pygame.KEYDOWN):
            if event.key == self.k_slap:
                self.slap()
            if event.key == self.k_dodge:
                self.dodge()
            if event.key == self.k_feint:
                self.feint()

    def state_slap(self):
        self.image = self.sprites.slap.play(self.animation_frame)
        if not self.image:
            self.image = self.sprites.stand.play(0)
            self.state = self.state_idle

    def state_dodge(self):
        self.image = self.sprites.dodge.play_once(self.animation_frame)
        if not pygame.key.get_pressed()[self.k_dodge] or self.tick > 40:
            self.state = self.state_dodge_recovery

    def state_dodge_recovery(self):
        self.image = self.sprites.dodge_recovery.play(self.animation_frame)
        if not self.image:
            self.image = self.sprites.stand.play(0)
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
