from math import inf

from numpy import array
from typing import TYPE_CHECKING, Tuple

from chess.constants import WHITE, BLACK

if TYPE_CHECKING:
    from .board import ChessBoard, Square

BISHOP_DIRECTIONS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
ROOK_DIRECTIONS = ((0, 1), (0, -1), (1, 0), (-1, 0))
KNIGHT_DIRECTIONS = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))


class Piece:
    team: str  # "white" or "black"
    letter: str  # "k" for king
    board: "ChessBoard"
    square: Tuple[int, int]
    directions: tuple  # what directions can this piece move
    strides: int  # how many squares can this piece move along its directions

    def __init__(self, team=WHITE):
        self.team = team

    def __str__(self):
        return self.letter.upper() if self.team == WHITE else self.letter.lower()

    def __repr__(self):
        string = f"{self.team} {self.__class__.__name__}"
        square = self.square
        if square:
            square = self.board.square_name(square)
            string += f" on {square}"
        return string

    def __eq__(self, other: "Piece"):
        return self.__class__ == other.__class__ and self.team == other.team

    @property
    def moves(self) -> set:
        """Set of squares this piece could move to, taking into account obstructions and board
        edges"""
        moves = set()
        for direction in self.directions:
            direction = array(direction)
            candidate = self.square
            ii = 0
            while candidate in self.board.squares and ii < self.strides:
                candidate = tuple(direction + candidate)
                moves.add(candidate)
                if self.board.contents.get(candidate):
                    break
                ii += 1

        return {
            move
            for move in moves
            if move in self.board.squares
            and (
                self.board.contents.get(move) is None  # empty squares
                or self.board.contents.get(move).team != self.team  # only capture enemies
            )
        }

    @property
    def square(self) -> "Square":
        """Coordinates of self on board"""
        try:
            return self.board.locate(self)
        except AttributeError:
            return None

    @classmethod
    def from_letter(cls, letter: str, *args, **kwargs):
        klass = CLASSES_BY_LETTER[letter.lower()]
        team = WHITE if letter.isupper() else BLACK
        return klass(*args, team=team, **kwargs)


class King(Piece):
    letter = "k"
    directions = ROOK_DIRECTIONS + BISHOP_DIRECTIONS
    strides = 1


class Queen(Piece):
    letter = "q"
    directions = ROOK_DIRECTIONS + BISHOP_DIRECTIONS
    strides = inf


class Bishop(Piece):
    letter = "b"
    directions = BISHOP_DIRECTIONS
    strides = inf


class Knight(Piece):
    letter = "n"
    directions = KNIGHT_DIRECTIONS
    strides = 1


class Rook(Piece):
    letter = "r"
    directions = ROOK_DIRECTIONS
    strides = inf


class Pawn(Piece):
    letter = "p"


CLASSES = [King, Queen, Rook, Bishop, Knight, Pawn]
CLASSES_BY_LETTER = {cls.letter: cls for cls in CLASSES}
