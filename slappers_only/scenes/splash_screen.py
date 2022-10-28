import pygame
from pygame.surface import Surface
from robingame.input import EventQueue
from robingame.objects import Entity, PhysicalEntity
from robingame.animation import ease_out, ease_in
from typing import Callable

from robingame.text.font import fonts

from slappers_only import images, conf


class SplashScreen(PhysicalEntity):
    blink_speed = 40
    draw_start_text = False

    def __init__(self, x, y, callback: Callable):
        super().__init__()
        self.callback = callback
        self.state = self.state_animate_in
        self.image = images.splash_screen.play(0)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = self.starting_y = 0
        self.target_y = y

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        if self.draw_start_text:
            fonts.cellphone_black.render(
                surface,
                text="Press any key to play",
                x=0,
                y=conf.WINDOW_HEIGHT * 7 // 8,
                scale=3,
                wrap=conf.WINDOW_WIDTH,
                align=0,
            )

    def state_animate_in(self):
        try:
            self.y = ease_out(start=self.starting_y, stop=self.target_y, num=30)[self.tick]
        except IndexError:
            self.state = self.state_idle

    def state_idle(self):
        if self.tick % self.blink_speed == 0:
            self.draw_start_text = not self.draw_start_text
        if EventQueue.filter(type=pygame.KEYDOWN):
            self.state = self.state_animate_out

    def state_animate_out(self):
        try:
            self.y = ease_in(start=self.target_y, stop=conf.WINDOW_HEIGHT, num=20)[self.tick]
        except IndexError:
            self.callback()
            self.kill()
