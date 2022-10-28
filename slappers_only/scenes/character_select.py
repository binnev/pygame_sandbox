import pygame
from robingame.input import EventQueue
from robingame.objects import Entity
from robingame.text.font import fonts

from slappers_only import conf
from slappers_only.events import SetValue


class CharacterSelectScreen(Entity):
    p1_value: int = 0
    p2_value: int = 0

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def draw(self, surface, debug=False):
        super().draw(surface, debug)
        fonts.cellphone_black.render(
            surface,
            text=f"{self.p1_value}",
            x=0,
            y=conf.WINDOW_HEIGHT // 2,
            scale=6,
            wrap=conf.WINDOW_WIDTH // 2,
            align=0,
        )
        fonts.cellphone_black.render(
            surface,
            text=f"{self.p2_value}",
            x=conf.WINDOW_WIDTH // 2,
            y=conf.WINDOW_HEIGHT // 2,
            scale=6,
            wrap=conf.WINDOW_WIDTH // 2,
            align=0,
        )

    def update(self):
        super().update()
        for event in EventQueue.filter(type=pygame.KEYDOWN):
            if event.key == pygame.K_d:
                self.p1_value += 1
            if event.key == pygame.K_a:
                self.p1_value -= 1
            if event.key == pygame.K_l:
                self.p2_value += 1
            if event.key == pygame.K_j:
                self.p2_value -= 1
            if event.key == pygame.K_ESCAPE:
                self.exit()

    def exit(self):
        self.callback()
        EventQueue.add(SetValue(p1=self.p1_value, p2=self.p2_value))
        self.kill()
