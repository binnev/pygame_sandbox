import sys

import pygame
from pygame.color import Color
from pygame.surface import Surface

from base.input import EventQueue
from base.objects import Game


class LangtonsAntGame(Game):
    fps = 0
    window_width = 600
    window_height = 600
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
                    print(f"self.ticks_per_frame: {self.ticks_per_frame}")
                if event.key == pygame.K_UP:
                    self.ticks_per_frame *= 2
                    print(f"self.ticks_per_frame: {self.ticks_per_frame}")

    def update(self):
        for _ in range(self.ticks_per_frame):
            super().update()

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        text_bitmap = self.font.render(f"iterations: {self.tick}", True, Color("black"))
        surface.blit(text_bitmap, (0, 0))
        text_bitmap = self.font.render(f"scaling: {self.board.scaling}", True, Color("black"))
        surface.blit(text_bitmap, (0, 30))
