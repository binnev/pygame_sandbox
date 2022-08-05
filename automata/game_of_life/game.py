from pygame import Color

from automata.game import AutomataGame
from automata.game_of_life import patterns


class GameOfLife(AutomataGame):
    fps = 60
    window_width = 1200
    window_height = 1200
    window_caption = "Conway's Game of Life"
    screen_color = Color("gray")
    ticks_per_frame = 1

    def __init__(self):
        super().__init__()
        from automata.game_of_life.classes import InfiniteBoard

        self.board = InfiniteBoard({coord: True for coord in patterns.INFINITE_GROWER_1HIGH})
        self.add_scene(self.board)


if __name__ == "__main__":
    GameOfLife().main()
