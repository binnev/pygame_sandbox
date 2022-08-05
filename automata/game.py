import sys
import time

import pygame
from pygame import Surface, Color

from base.input import EventQueue
from base.objects import Game


class AutomataGame(Game):
    fps = 0  # run as fast as possible
    ticks_per_frame: int = 1  # how many iterations to do between draws

    def update(self):
        t1 = time.perf_counter()
        for _ in range(self.ticks_per_frame):
            super().update()
        t2 = time.perf_counter()
        print(f"update time = {t2-t1}")

    def draw(self, surface: Surface, debug: bool = False):
        t1 = time.perf_counter()
        super().draw(surface, debug)
        text_bitmap = self.font.render(f"iterations: {self.tick}", True, self.debug_color)
        surface.blit(text_bitmap, (0, 0))
        text_bitmap = self.font.render(f"scaling: {self.board.scaling}", True, self.debug_color)
        surface.blit(text_bitmap, (0, 30))
        text_bitmap = self.font.render(
            f"ticks per frame: {self.ticks_per_frame}", True, self.debug_color
        )
        surface.blit(text_bitmap, (0, 60))
        text_bitmap = self.font.render(
            f"fps: {self.fps}", True, self.debug_color
        )
        surface.blit(text_bitmap, (0, 90))
        t2 = time.perf_counter()
        print(f"draw time =   {t2-t1}")

    def read_inputs(self):
        super().read_inputs()
        for event in EventQueue.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_DOWN:
                    self.ticks_per_frame = max([1, self.ticks_per_frame // 2])
                if event.key == pygame.K_UP:
                    self.ticks_per_frame *= 2
