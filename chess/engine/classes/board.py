import string
from collections import namedtuple
from typing import Dict, Tuple

from chess.constants import WHITE, BLACK
from chess.engine.classes.piece import Piece, Rook, Knight, Bishop, Queen, King, Pawn
from chess.notation import (
    parse_pgn_move,
    parse_fen_string,
    parse_fen_position,
    generate_fen_position,
)

Square = namedtuple("Square", "x y")


class ChessBoard:
    contents: Dict[Square, Piece]
    height: int = 8
    width: int = 8
    current_player: str = WHITE

    def __init__(self, height=None, width=None):
        self.contents = dict()
        self.height = height if height else self.height
        self.width = width if width else self.width
        self.squares = tuple(Square(x, y) for y in range(self.height) for x in range(self.width))

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
        # todo: read current player from FEN
        position, *_ = parse_fen_string(string)
        pieces = parse_fen_position(position)
        # using add_piece here makes sure the piece gets a ref to board.
        for square, piece in pieces.items():
            self.add_piece(piece, square)

    @property
    def fen_position(self):
        return generate_fen_position(self.contents)

    def do_pgn_move(self, string):
        piece_class, specifier, capture, square_name = parse_pgn_move(string)
        target_square = self.square_coords(square_name)
        candidate_pieces = [
            piece
            for coords, piece in self.contents.items()
            if isinstance(piece, piece_class)
            and target_square in piece.moves
            and piece.team == self.current_player
        ]
        if specifier:
            if specifier.isnumeric():
                y = self.number_to_y(specifier)
                candidate_pieces = [piece for piece in candidate_pieces if piece.square.y == y]
            else:
                x = self.letter_to_x(specifier)
                candidate_pieces = [piece for piece in candidate_pieces if piece.square.x == x]

        piece = candidate_pieces[0]
        self.move_piece(piece.square, target_square)

    def add_piece(self, piece: Piece, square: Square):
        square = Square(*square)
        self.contents[square] = piece
        piece.board = self

    def remove_piece(self, square: Square):
        del self.contents[square]

    def move_piece(self, square1: Square, square2: Square):
        self.contents[square2] = self.contents.pop(square1)

    def __str__(self, V_SEP="\n", H_SEP=" "):
        xs = range(self.width)
        ys = range(0, -self.height, -1)
        return V_SEP.join(
            H_SEP.join(str(self.contents.get((x, -y), ".")) for x in range(min(xs), max(xs) + 1))
            for y in range(min(ys), max(ys) + 1)
        )

    @classmethod
    def number_to_y(cls, number: str):
        return int(number) - 1

    @classmethod
    def letter_to_x(cls, letter: str):
        return string.ascii_lowercase.index(letter)

    @classmethod
    def square_coords(cls, name: str):
        """
        a1 -> (0, 0)
        h8 -> (7, 7)
        """
        letter, number = name.lower()
        x = cls.letter_to_x(letter)
        y = cls.number_to_y(number)
        return (x, y)

    @classmethod
    def y_to_number(cls, y: int):
        return str(y + 1)

    @classmethod
    def x_to_letter(cls, x: int):
        return string.ascii_lowercase[x]

    @classmethod
    def square_name(cls, square: Square):
        """
        (0, 0) -> a1
        (7, 7) -> h8
        """
        x, y = square
        number = cls.y_to_number(y)
        letter = cls.x_to_letter(x)
        return letter + number

    def locate(self, piece: Piece) -> Square:
        """Get coordinates of Piece instance"""
        for coords, p in self.contents.items():
            if p is piece:
                return Square(*coords)

    def pawn_starting_squares(self, team):
        return (
            [Square(x, 1) for x in range(self.width)]
            if team == WHITE
            else [Square(x, self.height - 2) for x in range(self.width)]
        )
