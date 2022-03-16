from base.objects import Entity
from quarto.assets.pieces import quarto_pieces


class Piece(Entity):
    tall: bool
    hollow: bool
    square: bool
    black: bool

    def __init__(self, x: int, y: int, tall: bool, hollow: bool, square: bool, black: bool):
        super().__init__()
        self.x = x
        self.y = y
        self.tall = tall
        self.hollow = hollow
        self.square = square
        self.black = black

        # todo: set correct self.image
        self.image = quarto_pieces["tall-hollow-square-white"].play(0)


