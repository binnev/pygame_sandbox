import pygame
from pygame.surface import Surface
from robingame.animation import ease_out, ease_in
from robingame.objects import Entity, Group
from robingame.text.font import fonts
from typing import Callable

from slappers_only import sounds, conf
from slappers_only.objects import Character


class SlappersOnlyScene(Entity):
    def __init__(self):
        super().__init__()
        self.characters = Group()
        self.gui_elements = Group()
        self.characters.add(Character(x=100, y=100))
        self.characters.add(Character(x=180, y=100, facing_right=False))

        self.child_groups = [
            self.characters,
        ]

    def update(self):
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
                p2.state = p2.state_get_hit
                sounds.slap2.play()
            if p2.state.__name__ == "state_slap" and p1.state.__name__ != "state_get_hit":
                p1.state = p1.state_get_hit
                sounds.slap2.play()

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
