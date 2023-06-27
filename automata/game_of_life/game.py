from pygame import Color
from robingame.objects import Game

from automata.game_of_life.scene import GameOfLifeScene


class GameOfLife(Game):
    fps = 64
    window_width = 600
    window_height = 600
    window_caption = "Conway's Game of Life"
    screen_color = Color("black")
    debug_color = Color("white")
    debug = False

    def __init__(self):
        super().__init__()
        self.scenes.add(GameOfLifeScene())


if __name__ == "__main__":
    GameOfLife().main()
