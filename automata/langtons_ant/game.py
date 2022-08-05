import sys
import time

import pygame
from pygame.color import Color
from pygame.surface import Surface

from base.input import EventQueue
from base.objects import Game


class LangtonsAntGame(Game):
    fps = 0
    window_width = 1200
    window_height = 1200
    window_caption = "Langton's Ant Simulator"
    font_name = "ubuntu"
    font_size = 20
    parental_name = "game"
    ticks_per_frame = 256  # how many iterations to do between draws
    screen_color = Color("white")

    def __init__(self):
        super().__init__()
        from automata.langtons_ant.classes import Board

        self.board = Board(self)
        self.add_scene(self.board)

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

    def update(self):
        t1 = time.perf_counter()
        for _ in range(self.ticks_per_frame):
            super().update()
        t2 = time.perf_counter()
        print(f"update time = {t2-t1}")


    def draw(self, surface: Surface, debug: bool = False):
        t1 = time.perf_counter()
        super().draw(surface, debug)
        text_bitmap = self.font.render(f"iterations: {self.tick}", True, Color("black"))
        surface.blit(text_bitmap, (0, 0))
        text_bitmap = self.font.render(f"scaling: {self.board.scaling}", True, Color("black"))
        surface.blit(text_bitmap, (0, 30))
        text_bitmap = self.font.render(
            f"ticks per frame: {self.ticks_per_frame}", True, Color("black")
        )
        surface.blit(text_bitmap, (0, 60))
        t2 = time.perf_counter()
        print(f"draw time =   {t2-t1}")

