import string
from typing import Dict, Tuple

from chess.constants import WHITE, BLACK
from chess.engine.classes.piece import Piece, Rook, Knight, Bishop, Queen, King, Pawn
from chess.notation import parse_fen_position


class ChessBoard:
    contents: Dict[Tuple[int, int], Piece]
    height: int = 8
    width: int = 8

    def __init__(self, height=None, width=None):
        self.contents = dict()
        self.height = height if height else self.height
        self.width = width if width else self.width
        self.squares = tuple((x, y) for y in range(self.height) for x in range(self.width))

    def load_standard_setup(self):
        self.add_piece(Rook(WHITE), (0, 0))
        self.add_piece(Knight(WHITE), (1, 0))
        self.add_piece(Bishop(WHITE), (2, 0))
        self.add_piece(Queen(WHITE), (3, 0))
        self.add_piece(King(WHITE), (4, 0))
        self.add_piece(Bishop(WHITE), (5, 0))
        self.add_piece(Knight(WHITE), (6, 0))
        self.add_piece(Rook(WHITE), (7, 0))
        self.add_piece(Rook(BLACK), (0, 7))
        self.add_piece(Knight(BLACK), (1, 7))
        self.add_piece(Bishop(BLACK), (2, 7))
        self.add_piece(Queen(BLACK), (3, 7))
        self.add_piece(King(BLACK), (4, 7))
        self.add_piece(Bishop(BLACK), (5, 7))
        self.add_piece(Knight(BLACK), (6, 7))
        self.add_piece(Rook(BLACK), (7, 7))
        for x in range(8):
            self.add_piece(Pawn(WHITE), (x, 1))
            self.add_piece(Pawn(BLACK), (x, 6))

    def load_fen_position(self, string):
        pieces, *_ = parse_fen_position(string)
        self.contents = pieces

    def add_piece(self, piece: Piece, square: Tuple[int, int]):
        self.contents[square] = piece
        piece.board = self

    def remove_piece(self, square: Tuple[int, int]):
        del self.contents[square]

    def move_piece(self, square1, square2):
        self.contents[square2] = self.contents.pop(square1)

    def __str__(self):
        V_SEP = "\n"
        H_SEP = " "
        xs = range(self.width)
        ys = range(0, -self.height, -1)
        return V_SEP.join(
            H_SEP.join(str(self.contents.get((x, -y), ".")) for x in range(min(xs), max(xs) + 1))
            for y in range(min(ys), max(ys) + 1)
        )

    def square_coords(self, name: str):
        """
        a1 -> (0, 0)
        h8 -> (7, 7)
        """
        name = name.lower()
        x, y = name
        y = int(y) - 1
        x = string.ascii_lowercase.index(x)
        return (x, y)

    def square_name(self, square: Tuple[int, int]):
        """
        (0, 0) -> a1
        (7, 7) -> h8
        """
        x, y = square
        y = str(y + 1)
        x = string.ascii_lowercase[x]
        return x + y

    def locate(self, piece: Piece) -> tuple:
        for coords, p in self.contents.items():
            if p is piece:
                return coords
