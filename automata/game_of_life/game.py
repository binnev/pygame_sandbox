from pygame import Color

from automata.game import AutomataGame
from automata.game_of_life import patterns
from automata.game_of_life.patterns import load_pattern


class GameOfLife(AutomataGame):
    fps = 30
    window_width = 1200
    window_height = 1200
    window_caption = "Conway's Game of Life"
    screen_color = Color("black")
    ticks_per_frame = 1
    debug_color = Color("white")

    def __init__(self):
        super().__init__()
        from automata.game_of_life.classes import InfiniteBoard

        self.board = InfiniteBoard(
            {
                **load_pattern(patterns.ACORN),
                # **load_pattern(patterns.HEAVY_SPACESHIP, shift=(0, 50)),
                # **load_pattern(patterns.MEDIUM_SPACESHIP, shift=(0, 60)),
                # **load_pattern(patterns.LIGHTWEIGHT_SPACESHIP, shift=(0, 70)),
                # **load_pattern(patterns.INFINITE_GROWER2, shift=(0, 100)),
            }
        )
        self.add_scene(self.board)


if __name__ == "__main__":
    GameOfLife().main()
