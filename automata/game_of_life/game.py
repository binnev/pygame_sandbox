from pygame import Color

from automata.game import AutomataGame


class GameOfLife(AutomataGame):
    fps = 60
    window_caption = "Conway's Game of Life"
    screen_color = Color("gray")
    ticks_per_frame = 1

    def __init__(self):
        super().__init__()
        from automata.game_of_life.classes import InfiniteBoard

        self.board = InfiniteBoard(
            {
                coord: True
                for coord in [
                    (0, 0),
                    (2, 0),
                    (4, 0),
                    (1, 1),
                    (2, 1),
                    (4, 1),
                    (3, 2),
                    (4, 2),
                    (0, 3),
                    (0, 4),
                    (1, 4),
                    (2, 4),
                    (4, 4),
                ]
            }
        )
        self.add_scene(self.board)


if __name__ == "__main__":
    GameOfLife().main()
