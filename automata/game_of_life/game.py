from collections import deque

import pygame
from pygame import Color

from automata.game import AutomataGame
from automata.game_of_life import patterns
from automata.game_of_life.patterns import load_pattern
from base.input import EventQueue


class GameOfLife(AutomataGame):
    fps = 64
    window_width = 1200
    window_height = 800
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
        self.history = deque(maxlen=50)

    def read_inputs(self):
        super().read_inputs()
        for event in EventQueue.events:
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_SPACE:
                        raise NextGame

    def update(self):
        super().update()
        if not self.board.contents:
            raise NextGame

        for h in self.history:
            if set(self.board.contents) == h:
                raise NextGame

        self.history.append(set(self.board.contents))


class NextGame(Exception):
    pass


if __name__ == "__main__":
    """
    Interesting ones:
    (u, o, r)
    351 lots of squares
    042 static crystal
    142 static crystal 2
    242 crystal with marching ants
    332 lots of glider like things
    342 lots of glider like things
    032 constant activity; slow growing (133, 243)
    043 maze-like circle (143)
    053 fungal with staircase features
    064 fungal with vertical highways (163, 263, 373)
    073 fungal with horizontal highways (173, 183, 273, 283, 383)
    153 eye of sauron, staircase features
    253 self-similar fractal growth
    363 snowflake like growth
    353 extremely slow growing, rippling edges (483)
    """
    for r in range(9):
        for u in range(9):
            for o in range(9):
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
