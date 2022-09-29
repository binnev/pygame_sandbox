import sys
import time

import pygame
from pygame import Surface

from robingame.input import EventQueue
from robingame.objects import Game
from robingame.text.font import fonts


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
        text = "\n".join(
            [
                f"iterations: {self.tick}",
                f"scaling: {self.board.scaling}",
                f"ticks per frame: {self.ticks_per_frame}",
                f"fps: {self.fps}",
            ]
        )
        fonts.cellphone_white.render(surface, text, scale=2)
        t2 = time.perf_counter()
        print(f"draw time =   {t2-t1}")

    def read_inputs(self):
        super().read_inputs()
        for event in EventQueue.events:
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    case pygame.K_DOWN:
                        self.ticks_per_frame = max([1, self.ticks_per_frame // 2])
                    case pygame.K_UP:
                        self.ticks_per_frame *= 2
                    case pygame.K_RIGHT:
                        self.fps *= 2
                    case pygame.K_LEFT:
                        self.fps = max(1, self.fps // 2)
