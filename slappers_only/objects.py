import pygame
from robingame.objects import PhysicalEntity

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
        self.input = KeyboardPlayer1() if facing_right else KeyboardPlayer2()
        self.state = self.state_idle
        self.sprites = character_sprites if facing_right else character_sprites_flipped

    def update(self):
        super().update()
        self.input.read_new_inputs()

    def state_idle(self):
        self.image = self.sprites.stand.loop(self.animation_frame)
        if self.input.slap.is_pressed:
            self.slap()
        if self.input.dodge.is_pressed:
            self.dodge()
        if self.input.feint.is_pressed:
            self.feint()

    def state_windup(self):
        self.image = self.sprites.windup.play_once(self.animation_frame)
        if self.tick > 10 and (not self.input.slap.is_down or self.tick > 40):
            self.state = self.state_slap

    def state_slap(self):
        self.image = self.sprites.slap.play(self.animation_frame)
        if not self.image:
            self.image = self.sprites.stand.play(0)
            self.state = self.state_idle

    def state_dodge(self):
        self.image = self.sprites.dodge.play_once(self.animation_frame)
        if not self.input.dodge.is_down or self.tick > 40:
            self.state = self.state_dodge_recovery

    def state_dodge_recovery(self):
        self.image = self.sprites.dodge_recovery.play(self.animation_frame)
        if not self.image:
            self.image = self.sprites.stand.play(0)
            self.state = self.state_idle

    def state_get_hit(self):
        self.image = self.sprites.gethit.play(self.animation_frame)
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
        self.state = self.state_windup

    def dodge(self):
        print("dodge")
        self.state = self.state_dodge

    def feint(self):
        print("feint")
