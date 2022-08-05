from pygame.color import Color

from automata.game import AutomataGame


class LangtonsAntGame(AutomataGame):
    window_width = 1200
    window_height = 1200
    window_caption = "Langton's Ant Simulator"
    font_name = "ubuntu"
    font_size = 20
    parental_name = "game"
    ticks_per_frame = 512
    screen_color = Color("white")

    def __init__(self):
        super().__init__()
        from automata.langtons_ant.classes import Board

        self.board = Board(self)
        self.add_scene(self.board)


if __name__ == "__main__":
    LangtonsAntGame().main()