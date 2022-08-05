import pygame
from pygame import Color

from automata.game import AutomataGame
from automata.game_of_life import patterns
from automata.game_of_life.patterns import load_pattern
from base.input import EventQueue


class GameOfLife(AutomataGame):
    fps = 64
    window_width = 1200
    window_height = 1200
    window_caption = "Conway's Game of Life"
    screen_color = Color("black")
    ticks_per_frame = 1
    debug_color = Color("white")
    debug = True

    def __init__(self, **kwargs):
        super().__init__()
        from automata.game_of_life.classes import InfiniteBoard

        self.board = InfiniteBoard(
            {
                **load_pattern(patterns.BLOCK),
                # **load_pattern(patterns.HEAVY_SPACESHIP, shift=(0, 50)),
                # **load_pattern(patterns.MEDIUM_SPACESHIP, shift=(0, 60)),
                # **load_pattern(patterns.LIGHTWEIGHT_SPACESHIP, shift=(0, 70)),
                # **load_pattern(patterns.INFINITE_GROWER2, shift=(0, 100)),
            },
            **kwargs,
        )
        self.add_scene(self.board)

    def read_inputs(self):
        super().read_inputs()
        for event in EventQueue.events:
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_SPACE:
                        raise NextGame()


class NextGame(Exception):
    pass


if __name__ == "__main__":
    for o in range(9):
        for u in range(9):
            for r in range(9):
                if u > o:
                    continue
                try:
                    GameOfLife(
                        overpopulation_threshold=o,
                        underpopulation_threshold=u,
                        reproduction_threshold=r,
                    ).main()
                except NextGame:
                    pass
