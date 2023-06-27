from pygame import Color
from robingame.objects import Game

from automata.langtons_ant.scene import LangtonsAntScene


class LangtonsAnt(Game):
    fps = 64
    window_width = 600
    window_height = 600
    window_caption = "Langton's Ant"
    screen_color = Color("black")
    debug_color = Color("white")
    debug = False

    def __init__(self):
        super().__init__()
        self.scenes.add(LangtonsAntScene())


if __name__ == "__main__":
    LangtonsAnt().main()
