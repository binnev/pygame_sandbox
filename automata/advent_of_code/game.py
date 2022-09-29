import pygame
from pygame.color import Color
from pygame.surface import Surface

from robingame.input import EventQueue
from robingame.objects import Game


class AdventOfCodeGame(Game):
    fps = 60
    window_width = 1000
    window_height = 1000
    window_caption = "Advent of Code"
    font_name = "ubuntu"
    font_size = 20
    parental_name = "game"
    ticks_per_frame = 1  # how many iterations to do between draws
    screen_color = Color("black")

    def __init__(self):
        super().__init__()
        from automata.advent_of_code.menus import MainMenu

        self.add_scene(MainMenu())

    def read_inputs(self):
        super().read_inputs()
        for event in EventQueue.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.fps = max([1, self.fps // 2])
                    print(f"self.fps: {self.fps}")
                if event.key == pygame.K_UP:
                    self.fps *= 2
                    print(f"self.fps: {self.fps}")

    def update(self):
        for _ in range(self.ticks_per_frame):
            super().update()

    def draw(self, surface: Surface, debug: bool = False):
        super().draw(surface, debug)
        text_bitmap = self.font.render(f"iterations: {self.tick}", True, Color("black"))
        surface.blit(text_bitmap, (0, 0))
