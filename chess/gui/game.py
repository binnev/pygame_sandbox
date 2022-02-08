from base.objects import Game
from chess.gui.scenes import ChessMatch


class ChessGame(Game):
    fps = 60
    window_width = 1000
    window_height = 1000
    window_caption = "chess"
    font_name = "ubuntu"
    font_size = 50
    parental_name = "game"

    def __init__(self):
        super().__init__()
        self.add_scene(ChessMatch())
