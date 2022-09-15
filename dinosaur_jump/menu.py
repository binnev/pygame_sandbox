import pygame
from pygame import Surface

from base.animation import ease_in_out, ease_in, ease_out
from base.gui.button import Button
from base.gui.menu import Menu
from base.input import EventQueue
from base.text.font import fonts
from dinosaur_jump import conf


class PauseMenu(Menu):
    def __init__(self):
        super().__init__()
        self.buttons.add(Button(0, 0, 100, 50, "test"))
        self.pause_text_y = 0
        self.state = self.state_animate_in

    def draw(self, surface: Surface, debug: bool = False):
        fonts.cellphone_white.render(
            surface,
            "PAUSED",
            x=0,
            y=self.pause_text_y,
            wrap=conf.WINDOW_WIDTH,
            align=0,
            scale=5,
        )

    def state_animate_in(self):
        self.pause_text_y = ease_out(start=-35, stop=10, num=15)[self.tick]
        if self.tick == 14:
            self.state = self.state_idle

    def state_animate_out(self):
        self.pause_text_y = ease_in(start=self.pause_text_y, stop=-35, num=15)[self.tick]
        if self.tick == 14:
            self.kill()

    def state_idle(self):
        if EventQueue.filter(type=pygame.KEYDOWN, key=pygame.K_ESCAPE):
            self.state = self.state_animate_out
