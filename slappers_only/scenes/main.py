from typing import Callable

import pygame
from pygame.surface import Surface
from robingame.animation import ease_out, ease_in
from robingame.input import EventQueue
from robingame.objects import Entity, Group
from robingame.text.font import fonts

from slappers_only import sounds, conf, images
from slappers_only.events import UpdateScore, GameOver
from slappers_only.objects import Character


class SlappersOnlyScene(Entity):
    p1_score = 0
    p2_score = 0
    win_condition = 3
    paused = False

    def __init__(self):
        super().__init__()
        self.characters = Group()
        self.gui_elements = Group()
        self.characters.add(
            Character(
                x=conf.WINDOW_WIDTH // 2 - 40,
                y=conf.WINDOW_HEIGHT // 2,
            )
        )
        self.characters.add(
            Character(
                x=conf.WINDOW_WIDTH // 2 + 40,
                y=conf.WINDOW_HEIGHT // 2,
                facing_right=False,
            )
        )

        self.child_groups = [
            self.characters,
        ]

    def draw(self, surface, debug=False):
        img = images.background_desert.loop(self.tick // 5)
        surface.blit(img, img.get_rect())
        super().draw(surface, debug)

    def update(self):
        if self.paused:
            return
        super().update()
        p1, p2 = self.characters
        collision = pygame.sprite.collide_mask(p1, p2)
        if collision:
            if p1.state.__name__ == p2.state.__name__ == "state_slap":
                p1.state = p1.state_idle
                p2.state = p2.state_idle
                sounds.metal_clang.play()
                print("clang")
            if p1.state.__name__ == "state_slap" and p2.state.__name__ != "state_get_hit":
                self.p1_score += 1
                p2.state = p2.state_get_hit
                EventQueue.add(UpdateScore(p1=self.p1_score, p2=self.p2_score))
                sounds.slap2.play()
            if p2.state.__name__ == "state_slap" and p1.state.__name__ != "state_get_hit":
                self.p2_score += 1
                p1.state = p1.state_get_hit
                EventQueue.add(UpdateScore(p1=self.p1_score, p2=self.p2_score))
                sounds.slap2.play()
            if self.p1_score == self.win_condition:
                EventQueue.add(GameOver("Player 1"))
            if self.p2_score == self.win_condition:
                EventQueue.add(GameOver("Player 2"))

            print("collision")


class FlyingGuiMixin(Entity):
    start_x: int
    start_y: int
    target_x: int
    target_y: int
    state_idle: Callable
    animation_duration: int = 15

    def __init__(self):
        super().__init__()
        self.state = self.state_animate_in

    def state_animate_in(self):
        self.y = ease_out(start=self.start_y, stop=self.target_y, num=self.animation_duration)[
            self.tick
        ]
        if self.tick == self.animation_duration - 1:
            self.state = self.state_idle

    def state_animate_out(self):
        self.y = ease_in(start=self.target_y, stop=self.start_y, num=self.animation_duration)[
            self.tick
        ]
        if self.tick == self.animation_duration - 1:
            self.kill()

    def state_idle(self):
        pass

    def exit(self):
        self.state = self.state_animate_out


class Toast(FlyingGuiMixin):
    def __init__(self, text, y=10, from_above=True, font=fonts.cellphone_white, **font_params):
        super().__init__()
        self.from_above = from_above
        self.target_y = y
        self.start_y = -35 if from_above else conf.WINDOW_HEIGHT + 20
        self.text = text
        self.font = font
        self.font_params = font_params

    def draw(self, surface: Surface, debug: bool = False):
        params = dict(wrap=conf.WINDOW_WIDTH, align=0, scale=5)
        params.update(self.font_params)
        self.font.render(surface, text=self.text, x=0, y=self.y, **params)
